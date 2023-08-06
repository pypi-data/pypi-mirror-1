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

#ifndef WEIGHTS_H
#define WEIGHTS_H

#include "fLayersGeneral.h" 

///  \class Weights Params.h "Core/Params.h" 
///  \brief Weights represent a set of parameters. 
class Weights
{
public:
  Weights(string name_,uint size,real lr_,real dc_);
  //name representing this set of parameters
  string name;
  //name of the class
  string classname;
  //nb of parameters
  uint n;
  //pointer to the parameters array
  real *w;
  //pointer to updates (gradient)
  real *wu;
  //start learning rate
  real start_lr;
  //learning rate
  real lr;
  //decrease constant
  real dc;
  ///backprop activation
  bool do_bprop;
  ///fowardprop activation
  bool do_fprop;
  virtual void setfbprop(bool do_fprop_,bool do_bprop_)
    {do_fprop=do_fprop_;do_bprop=do_bprop_;};
  void randomInit(real max);
  void clearUpdates(){memset(wu,0,n*sizeof(real));};//set updates to 0
  void perturb(real fraction,bool extremum);
  Weights* clone(){Weights *cw=new Weights(name,n,lr,dc);memcpy(w,cw->w,n*sizeof(real));return cw;};
  void copy(Weights *new_w){memcpy(w,new_w,n*sizeof(real));};
  virtual void multiplyLrBy(real factor){start_lr*=factor;};
  virtual void initEpoch(int i){lr=start_lr/(1+dc*i);};
  virtual ~Weights(){free(w);free(wu);};
};
ostream& operator<<(ostream& out,Weights& w);

///  \class LrWeights Weights.h "Core/Weights.h" 
///  \brief LrWeights represent a set of parameters with a specific lr for each parameters.
///
/// WARNING: if you want to use this class change Layer class hierarchy to Layer: public LrWeights

class LrWeights : public Weights
{
 public:
  LrWeights(string name_,uint size,real lr_,real dc_);
  real *old_weights_updates; 
  real *old_weights;
  real *lrs;
  real inc_factor;
  real dec_factor;
  void updateParamsLr();
  void memAlloc();
  void memFree();  
  virtual void initEpoch(int i);
  virtual ~LrWeights();
};
#endif
