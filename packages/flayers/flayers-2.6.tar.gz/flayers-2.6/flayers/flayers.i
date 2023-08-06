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

# Documentation reference
# http://www.swig.org/Doc1.3/Python.html

%module flayers 
%{
# include "flayers.h"
%}

# create a wrapper for input (int argc, char **argv) so you don t have to send to count
%typemap(in) (int argc, char **argv) {
  /* Check if is a list */
  if (PyList_Check($input)) {
    int i;
    $1 = PyList_Size($input);
    $2 = (char **) malloc(($1+1)*sizeof(char *));
    for (i = 0; i < $1; i++) {
      PyObject *o = PyList_GetItem($input,i);
      if (PyString_Check(o))
	$2[i] = PyString_AsString(PyList_GetItem($input,i));
      else {
	PyErr_SetString(PyExc_TypeError,"list must contain strings");
	free($2);
	return NULL;
      }
    }
    $2[i] = 0;
  } else {
    PyErr_SetString(PyExc_TypeError,"not a list");
    return NULL;
  }
}

%typemap(freearg) (int argc, char **argv) {
  free((char *) $2);
}
%include "carrays.i"
%array_class(float,floatArray);

class PyTrainer
{
public:
    PyTrainer(Trainer* trainer, ArgvParserContainer* apc);
    float train(int n_epochs,int batch_size=1);
    void save(char* filename);
    float fprop(float *input);
    float test(char type);
    float prob(int i);
    int n_inputs();
    int n_outputs();
    void usage();
    void displayfbprop();
};

# example: usage fexp["fexp","/","-e","10","-h","10","--oh","--lsm","-l","0.01"]
PyTrainer* _fexp(int argc, char** argv);
PyTrainer* loadTrainer(char *filename,char *override_base_dir);
float PyTrainer::train(int n_epochs,int batch_size);
void PyTrainer::save(char* filename);
float PyTrainer::test(char type='t');
float PyTrainer::fprop(float *input);
