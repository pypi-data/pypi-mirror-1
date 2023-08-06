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

#ifndef TRAINER_UTIL_H
#define TRAINER_UTIL_H

#include "Trainer.h"
#include "ArgvParserContainer.h"
#include "ClassTopology.h"

bool testLoadSaveLayer(Trainer* trainer,ArgvParserContainer *apc);
bool compare(Trainer *trainer1,Trainer* trainer2,DataSet *dset);
void saveTrainer(string filename,Trainer* trainer,ArgvParserContainer* apc,string progname);
void CreateSplittedConnectionNN(Trainer *trainer,ClassTopology* class_topology,real lr,real dc,uint n_outputs,uint n_hiddens,string cost_type);
//you can get back the ArgvParserContainer with apc
Trainer* loadTrainer(string filename,ArgvParserContainer* &apc,char* override_base_dir=NULL);
Trainer* TrainerFactory(ArgvParserContainer *apc,bool open_outputfile=true);
void generateTestDataSet(Trainer* trainer,ArgvParserContainer *apc,string prog_name);
#endif

