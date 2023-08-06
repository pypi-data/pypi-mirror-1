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

#include "ArgvParser.h"
#include "fDataSet.h"

#ifndef PREDEFARGVPARSER
#define PREDEFARGVPARSER

// Definition of usual parameters : data_set,exp,inctopo,optOneHidden

//data_set
extern string data_set_description;
extern opt opts_data_set[];
extern noargopt noargopts_data_set[];
//neural network settings
extern string nn_description;
extern opt opts_nn[];
extern noargopt noargopts_nn_set[];
//optimal bprop settings
extern string optbprop_description;
extern opt opts_optbprop[];
extern noargopt noargopts_optbprop_set[];
//topology incremental
extern string inc_topo_description;
extern opt opts_inc_topo[];
//Booster
extern string boost_description;
extern opt boost_Opt[];
//EveryNEpochs
extern string every_description;
extern opt every_Opt[];

class NNArgvParser:public ArgvParser{
  typedef ArgvParser inherited;
 public:
  NNArgvParser()
    :ArgvParser("NN_SETTINGS",opts_nn,noargopts_nn_set,nn_description)
    {};
};

class BpropTypeArgvParser:public ArgvParser{
  typedef ArgvParser inherited;
 public:
  BpropTypeArgvParser()
    :ArgvParser("OPT_BPROP",opts_optbprop,noargopts_optbprop_set,optbprop_description)
    {};
};

class IncTopoArgvParser:public ArgvParser{
  typedef ArgvParser inherited;
 public:
  IncTopoArgvParser()
    :ArgvParser("INC_TOPO",opts_inc_topo,NULL,inc_topo_description)
    {};
};

class BoostArgvParser:public ArgvParser{
  typedef ArgvParser inherited;
 public:
  BoostArgvParser()
    :ArgvParser("BOOSTER",boost_Opt,NULL,boost_description)
    {};
};

class EveryNEpochsArgvParser:public ArgvParser{
  typedef ArgvParser inherited;
 public:
  EveryNEpochsArgvParser()
    :ArgvParser("EVERYNEPOCHS",every_Opt,NULL,every_description)
    {};
};

class DataSetArgvParser:public ArgvParser{
  typedef ArgvParser inherited;
 public:
  DataSet *train_set_;
  DataSet *valid_set_;
  DataSet *test_set_;
  real *data_;
  real *targets_;
  real *means;//means of train_set
  real *vars;//variance of train_set
  string db_name_;
  // Hook to override base_dir
  char* _override_base_dir;
  DataSetArgvParser()
    :ArgvParser("DATASET",opts_data_set,NULL/*noargopts_data_set*/,data_set_description)
    {train_set_=NULL;valid_set_=NULL;test_set_=NULL;_override_base_dir=NULL;};
  virtual void CoherenceParamsValuesChecker();
  virtual void parse(int argc,char* argv[]);
  string getStringDescriptor(bool short_descr=true,ofstream *output=NULL);
  void splitTrainValidTest();
  void printData();
  void save(string filename);
  bool loadData(string filename);
  void normalizeDataInputs();
  void normalizeTarget();
  //void Coherence(NNArgvParser* nn_settings);
  ~DataSetArgvParser();
};
#endif

