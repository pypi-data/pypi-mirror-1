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

#ifndef TOPO_H
#define TOPO_H

#include "fLayersGeneral.h"
#include "Layer.h"
#include "WeightsList.h"
///
///  \class Topology Topology.h "Core/Topology.h"
///  \brief Topology is Layers link by Connectors.
///
/// class Topology (one of the Core class of FLayers Neural Network Learning library)
/// A Topology define a series of Layers link together by Connectors.
///

// TODO add n min or max neurones
enum BpropType {STD, DEEP_FIRST, MAX_SENSITIVITY, MIN_SENSITIVITY};

class Topology
{
 public:
  Topology(Layer *in,Layer *out,bool adapt_lr=false,
		  real inc=1.1,real decr=0.7,
		  BpropType bprop_type=STD,bool force_all_upper_connections=false);
  ///input Layer
  Layer *inl;
  ///output Layer
  Layer *outl;
  ofstream params_out;
  ///contain a reference(pointers) to all parameters
  WeightsList params_list;
  ///middle Layers (incl and outl are not and SHOULD NOT be included in that list)
  list<Layer*>llayers;
  ///last fprop result
  real result;
  bool adapt_lr;
  real inc_lr_factor;
  real decr_lr_factor;
  ///use in chagetLr()
  real last_cost;
  ///start increase lr after start_inc decrease of cost
  real start_inc;
  ///counter use in adaptlr
  uint count;
  ///same has trainer->cost
  real cost;
  // type of bprop to apply
  BpropType bprop_type;
  // in first deep, force all upper connection
  bool force_all_upper_connections;

  void addToBack(Layer *layer){llayers.push_back(layer);};
  void addToFront(Layer *layer){llayers.push_front(layer);};
  void multiplyLrBy(real factor);
  void setLr(real new_lr);
  void adaptLr(int i);
  virtual real fprop(bool apply=true);
  virtual void displayfprop(bool all=false);
  virtual void displaybprop(bool all=false);
  virtual void bprop(real target, bool stochastic=true);
  virtual void stdBprop(real target, bool stochastic=true);
  virtual void deepFirstBprop(real target, bool stochastic);
  virtual void sortSensitivityBprop(real target, bool stochastic, bool max=true);
  virtual void update(uint batch_size);
  virtual void fillUp(bool in2out=true);
  virtual void setfbprop(bool do_fprop=true, bool do_bprop=true);
  void saveParams(ofstream *out){(*out)<<params_list;};
  void loadParams(ifstream *in){(*in)>>params_list;};
  void openParamsFile(string name, uint n_epochs, bool octave=true);
  ///this fct is call before each epochs training; when overwrite, call it first
  void initEpoch(int i);
  virtual Connector* getConnector(string name);
  Layer *getLayer(string name);
  virtual ~Topology(){llayers.clear();params_list.cleanup();};
  };
typedef list<Topology*>::iterator TI;
#endif
