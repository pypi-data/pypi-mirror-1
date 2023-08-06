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

#ifndef INC_BOOST_TRAINER_H
#define INC_BOOST_TRAINER_H

#include "Trainer.h"
///  \class IncBoostTrainer IncBoostTrainerTrainer.h "Utils/IncBoostTrainerTrainer.h"
///  \brief IncBoostTrainer to speedup Incremental unchange parameters (usefull in incremental Architecture).
///
/// class IncBoostTrainer
/// Idea :If you do not backpropagate on some Layers or Connectors,
///       you will lost precious time during fprop
///       to overcome this problem you should use BoostTrainer.
///


class IncBoostTrainer:public Trainer
{
 public:
  DataSet* bds;///boost dataset
  IncBoostTrainer(real *means, real *vars):Trainer(means,vars){bds=NULL;};
  void freeMem(){if(bds)delete(bds);bds=NULL;};
  void cleanBoostDataSetAndReactivate();
  void createBoostDataSet(DataSet *dset);
  void updateBoostDataSet(DataSet *dset);
  void newBoostDataSet(DataSet *dset){createBoostDataSet(dset);updateBoostDataSet(dset);};
  virtual real trainOrTest(DataSet *dset,bool do_train,uint batch_size);
  ~IncBoostTrainer(){freeMem();};
};
#endif
