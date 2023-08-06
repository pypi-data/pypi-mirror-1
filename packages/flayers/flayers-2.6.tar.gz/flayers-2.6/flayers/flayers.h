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

#include "src/Trainer.h"
#include "src/PreDefArgvParser.h"
#include "src/ArgvParserContainer.h"
class PyTrainer
{
public:
	PyTrainer(Trainer* trainer, ArgvParserContainer* apc);
	Trainer *trainer;
	ArgvParserContainer *apc;
	DataSetArgvParser* ds;
	NNArgvParser* nn;
	BpropTypeArgvParser* bproptypeargs;

	float train(int n_epochs,int batch_size=1);
	float test(char type);
	void save(char* filename);
	float fprop(float *input);
	float prob(int i){return Exp(trainer->topo->outl->p[i])*100;}
	int n_inputs(){return trainer->topo->inl->n;}
	int n_outputs(){return trainer->topo->outl->n;}
	void usage(){apc->usage();}
	void displayfbprop(){trainer->displayfbprop(true);}
	~PyTrainer();
};
// interface to flayers main entrance point
PyTrainer* _fexp(int argc, char* argv[]);
PyTrainer* loadTrainer(char * filename,char * override_base_dir);
