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

#ifndef CLASS_TOPO_H
#define CLASS_TOPO_H

#include "Topology.h"
#include "NNLayer.h"

///
///  \class ClassTopology ClassTopology.h "Core/ClassTopology.h" 
///  \brief ClassTopology where you have a Layer for each class (output).
///
class ClassTopology: public Topology
{
 public:
  ClassTopology(Layer *in,Layer *out);
  /// inside output layer
  Layer** class_i;
  real bprop_criterion;
  char bprop_type;///backpropagation type [o=one output at a time;c=only <criterion;else Topology->bprop()]
  void bpropOneOutputAtaTime(real target,bool stochastic);
  void bpropCriterion(real target,bool stochastic);
  void bpropOneHiddenAtaTime(real target,bool stochastic);
  virtual void displayfprop();
  virtual void displaybprop();
  virtual void fillUp(){};
  virtual void bprop(real target,bool stochastic);
  virtual void update(uint batch_size);
  virtual void setfbprop(bool do_fprop,bool do_bprop);
  virtual ~ClassTopology(){};
  };
typedef list<Topology*>::iterator TI;
#endif

