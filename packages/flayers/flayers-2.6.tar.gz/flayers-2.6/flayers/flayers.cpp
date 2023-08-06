// Copyright (C) 2001-2003, 2008-2009 Francis Piéraut <fpieraut@gmail.com>

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.

// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

#include "flayers.h"
#include <stdio.h>
#include "src/NNLayer.h"
#include "src/TrainerUtil.h"
#include <time.h>

Topology *gtopo;
bool STDOUT=false;
//--------------------------------------------------------------------------
// fexp : Simple Flayers Neural Network Experiment
//--------------------------------------------------------------------------
PyTrainer* _fexp(int argc, char** argv)
{
  // Arguments parsers
  DataSetArgvParser* ds=new DataSetArgvParser();
  NNArgvParser* nn=new NNArgvParser();
  BpropTypeArgvParser* bpt=new BpropTypeArgvParser();
  ArgvParserContainer *apc=new ArgvParserContainer(argv[0]);
  apc->add(ds);
  apc->add(nn);
  apc->add(bpt);
  ds->set('b',"");

  //Data parsing
  apc->parse(argc,argv);

  if(nn->getChar("pseudo_random")!='?')
	  srand(nn->getInt("pseudo_random"));

  if(nn->getBool("reel_random"))
  	srand( (unsigned)time( NULL) );

  //create appropriate trainer
  Trainer *trainer=TrainerFactory(apc);
  trainer->stdout_on=false;
  //save params
  if(nn->getBool("save_params"))
    trainer->topo->openParamsFile(trainer->output_filename,nn->getInt("n_epochs"),true);

  trainer->train(ds->train_set_,ds->test_set_,nn->getInt("n_epochs"),nn->getInt("batch_size"));
  // optional load/save checkup
  if(nn->getBool("load_save_test"))
    testLoadSaveLayer(trainer,apc);
  if(nn->getBool("save"))
    saveTrainer(trainer->output_filename+".save",trainer,apc,argv[0]);
  if (ds->getReal("test_f")>0){
    cout<<"test on test_set:"<<endl;
    trainer->test(ds->test_set_);
  }
  return new PyTrainer(trainer,apc);
}

PyTrainer* loadTrainer(char *filename, char *override_base_dir)
{
	ArgvParserContainer *apc = new ArgvParserContainer("pyLoadTrainer");
	Trainer* trainer = loadTrainer(filename, apc, override_base_dir);
	trainer->stdout_on=false;
	return new PyTrainer(trainer,apc);
}

float PyTrainer::train(int n_epochs,int batch_size)
{
	return (float)trainer->train(ds->train_set_,ds->test_set_,n_epochs,batch_size);
}

// train=t, test=T, validation=v
float PyTrainer::test(char type='t')
{
	switch ( type ){
	         case 'T':return trainer->test(ds->test_set_);break;
	         case 'v':return trainer->test(ds->valid_set_);break;
	         default:return trainer->test(ds->train_set_);
	      }
}
float PyTrainer::fprop(real* input)
{
	return trainer->fprop(input);
}
void PyTrainer::save(char* filename)
{
	saveTrainer(string(filename)+".save",this->trainer,this->apc,string("pySaveTrainer"));
}

PyTrainer::~PyTrainer()
 {
	//memory cleanup
	delete trainer;
	delete nn;
	delete apc;
}

PyTrainer::PyTrainer(Trainer* trainer, ArgvParserContainer* apc)
{
	this->trainer = trainer;
	this->apc = apc;
	this->ds = (DataSetArgvParser*)apc->getArgvParser("DATASET");
	ds->set('b',"Datasets/");
	this->nn = (NNArgvParser*)apc->getArgvParser("NN_SETTINGS");
	this->bproptypeargs = (BpropTypeArgvParser*)apc->getArgvParser("OPT_BPROP");
}
