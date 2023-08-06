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

#ifndef LAYER_H
#define LAYER_H
//#define LRWEIGHTS
#include "fLayersGeneral.h"
#include "math_util.h"
#include "WeightsList.h"
#include "Weights.h"

class Connector;//forward class declaration
class Topology;
///
///  \class Layer Layer.h "Core/Layer.h"
///  \brief Layer class is the abstract representation of the input/output/hiddenLayer of a Neural Network.
///
/// Layer is the Core class of fLayers2 neural network library
/// A Layer can be the input Layer (Input), the hidden Layers (SigmMSE,TanhMSE)
/// or the output Layer (SigmMSE,LogSoftMax,TanhMSE).See also NNLayer.h
/// author: Francis Pieraut; begin in july 2002
class Layer: public Weights
{
 public:
  Layer(string name_,uint size,real lr_,real dc_);
  Layer(Layer *from,uint start,uint size);
  // list of single neurons layer
  list<Layer*> lneurons;
  Layer** neurons;
  ///list connector to up;usfull for input layer;the list size should be equal to 1 if it is a hidden layer
  list<Connector*> lcup;
  ///list connector down
  list<Connector*> lcdown;
  ///Layer connection point
  real *p;
  ///targets
  real *targs;
  ///output sensitivity
  real *sensitivity;
  ///bias
  real *bias;
  ///bias updates (batch mode)
  real *bias_update;
  ///min target value
  real min_targ;
  ///max target value
  real max_targ;
  ///usefull in Correlation
  real mean_cost;
  //General functions to overwrite
  virtual void fprop();
  virtual void update(uint batch_size);
  void _biasbprop(bool stochastic);
  virtual void bprop(real target, bool stochastic);
  virtual void bpropDeepFirst(real target, bool stochastic);
  virtual void bpropOfConnector(bool stochastic);
  virtual void displayfprop(bool all=false);
  virtual void displaybprop(bool all=false);
#ifndef LRWEIGHTS
  virtual void updateOnFly(){real *ps=sensitivity;real* pb=bias;for(uint i=0;i<n;i++)(*pb++) -=(*ps++)* lr;};
#endif
#ifdef LRWEIGHTS
  virtual void updateOnFly(){real *plr=lrs;real *ps=sensitivity;real* pb=bias;for(uint i=0;i<n;i++)(*pb++) -=(*ps++)* (*plr++);};
#endif
  virtual void updateGradient(){real *ps=sensitivity;real* pbu=bias_update;for(uint i=0;i<n;i++)(*pbu++) +=(*ps++);};
  virtual void initEpoch(int i);
  virtual void multiplyLrBy(real factor);
  virtual void setLr(real new_lr);
  //specific functions
  real result();
  void addUpConnection(Connector* cup);
  void clearLayer(){memset(p,0,n*sizeof(real));};//set outputs to 0
  void clearBias(){memset(bias,0,n*sizeof(real));};//set bias to 0
  void ComputeOutputSensitivity(real target){PreComputeOutputSensitivity(target);ComputeOutputSensitivity();PostComputeOutputSensitivity(target);};
  void PreComputeOutputSensitivity(real target){memset(sensitivity,0,n*sizeof(real));if(n>1)targs[(int)target]=max_targ;else targs[0]=target;};
  void PostComputeOutputSensitivity(real target){if(n>1)targs[(int)target]=min_targ;};
  void ComputeHiddenSensitivity(Connector *cup=NULL);
  void _updateHiddenSensitivity(Connector * cup);
  void setTargets(){real* pt=targs;for(uint i=0;i<n;i++)*pt++=min_targ;};
  void setMinMax(real min,real max){min_targ=min;max_targ=max;setTargets();};
  ///WARNING: you should call Layer::apply() first ->BECAUSE you need to add the bias and others thing depending on the heritage.
  virtual void apply(){if(do_fprop){real *pb=bias;real* po=p;for(uint i=0;i<n;i++)(*po++)+=*pb++;}};
  virtual void multiplyByDerivative(){};
  virtual void ComputeOutputSensitivity(){};
  virtual void setfbprop(bool do_fprop_,bool do_bprop_);
  virtual void setfbpropDown(bool do_bprop_);
  virtual real computeCost(real target);
  Connector* getConnector(string name);
  virtual ~Layer(){free(p);free(targs);free(bias);free(bias_update);free(sensitivity);};
};
bool compare_output_sensitivity_max(const Layer *a,const Layer *b);
bool compare_output_sensitivity_min(const Layer *a,const Layer *b);

bool compare_output_sensitivity(const Layer *a,const Layer *b);
ostream& operator<<(ostream& out,Layer& layer);

///  \class Connector Connector.h "Core/Connector.h"
///  \brief a Connector is use to link 2 Layers.
class Connector: public Weights
{
 public:
  Connector(Layer *in,Layer *out,real lr=0.1,real dc=0,bool init_outl=true);
  ///input Layer
  Layer *inl;
  ///output Layer
  Layer *outl;
  ///the weights
  real *weights;
  ///gradient of each weights
  real *weights_updates;
  virtual void fprop();
  virtual void update(uint batch_size);
  virtual void bpropDeepFirst(real target, bool stochastic);
  virtual void bprop(bool stochastic);
  virtual void displayfprop(bool all=false);
  virtual void displaybprop(bool all=true);
  virtual void updateOnFly();
  virtual void updateGradient();
  void clearWeights(){memset(weights,0,outl->n*inl->n*sizeof(real));};
  virtual Connector* clone(){return new Connector(inl,outl,lr,dc);};
  virtual ~Connector(){weights=NULL;weights_updates=NULL;};
};
typedef list<Layer*>::iterator LI;
typedef list<Layer*>::reverse_iterator RLI;
typedef list<Connector*>::iterator CI;
typedef list<Connector*>::reverse_iterator RCI;
# include "Topology.h"

#endif
