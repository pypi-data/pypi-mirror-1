#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#  Copyright (C) 2001-2003, 2008-2009 Francis Piéraut <fpieraut@gmail.com>

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.

#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from subprocess import call
import os
data_path = os.path.join('datasets','digits')

def _recompile():
    ''' recompile flayers '''
    call(['swig','-python','-c++','%s.i' %'flayers'])
    call('python setup.py build_ext --inplace'.split(' '))
    print "reloading flayers module"
    reload(flayers) 
try:
    import flayers
except:
    _recompile()

TRAINER = None

def fexp(args_string='/ -e 2 -h 100 --oh --lsm -l .01 -p 0'):
    ''' string argument interface to fexp module; return a trainer '''
    args=['fexp']
    args.extend(args_string.split(' '))
    TRAINER = flayers._fexp(args)
    return TRAINER

oh_100_fname = os.path.join(data_path,'oh-100h.save')
def loadTrainer(filename = oh_100_fname, override_base_dir=None):
    ''' load trainer from filename '''
    override_base_dir = override_base_dir or ''
    if len(override_base_dir) and override_base_dir[-1] != '/':
        override_base_dir += '/'
    print "loading %s <%s>" %(filename, override_base_dir)
    TRAINER = flayers.loadTrainer(filename, override_base_dir)
    return TRAINER

def tofloats(inputs):
    finputs = flayers.floatArray(len(inputs))
    for i in range(len(inputs)):
        finputs[i]=inputs[i]
    return finputs

# WARNING: TRAINER assignation doesn't seems to work
def fprop(inputs, trainer=None):
    trainer = trainer or TRAINER
    if trainer:
        return trainer.fprop(tofloats(inputs))
    else:
        raise ("no trainer set")
     
if __name__ == "__main__":
    import unittest
    cost_map ={'oh-100h.save': -9196201.0}
    optprob_args='-d letters.1k.dat / -h 10 -e 5 --lsm -l .01 -p 0 '
               
    def get_cost(args_string):
        t = fexp(args_string)
        return round(t.test('t'))
    
    class flayerTests(unittest.TestCase):

        def test_load_save(self):
            fexp(optprob_args+"--oh --loadsave_test")
            
        def test_load(self):
            t = loadTrainer('oh-100h.save')
            self.assertEqual(t.test('t'),cost_map['oh-100h.save'])
          
        def test_fprop(self):
            t = loadTrainer()
            inputs=range(t.n_inputs())
            finputs=tofloats(inputs)
            self.assertEqual(t.fprop(finputs),4)
        
        def test_fprop2(self):
            t = loadTrainer()
            inputs = range(t.n_inputs())
            self.assertEqual(fprop(inputs,t),4)
        
        def test_prob(self):
            t = loadTrainer()
            fprop(range(t.n_inputs()),t)
            sum=0
            for i in range(t.n_outputs()):
                sum+=t.prob(i)
            if sum > 1.01 or sum<.99:
                raise ValueError("it doesn't sum to 1: %s" %sum)
   
        def test_ref_100h_letters(self):
            fname = 'test100.1e'
            self.assertEqual(get_cost('/ --oh -h 100 -e 1 --lsm -l .01 -p 0 -o %s' %fname),-5143084)
    
        def test_ref_optbrop(self):
            self.assertEqual(get_cost(optprob_args+'--oh'), -140076)
        
        def test_ref_opttopo(self):
            self.assertEqual(get_cost(optprob_args+'--opt'),-140799)
        
        def test_ref_opttopo_maxsens(self):
            self.assertEqual(get_cost(optprob_args+'--opt --maxsens'),-141047 )
        
        def test_ref_opttopo_maxsens_forcecup(self):
            self.assertEqual(get_cost(optprob_args+'--opt --maxsens --forceup'),-157085)
        
        def test_ref_opttopo_minsens(self):
            self.assertEqual(get_cost(optprob_args+'--opt --minsens'),-140573)
        
        def test_ref_opttopo_minsens_forcecup(self):
            self.assertEqual(get_cost(optprob_args+'--opt --minsens --forceup'),-152689)
       
    unittest.main()
