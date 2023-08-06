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

#ifndef NNLAYER_H
#define NNLAYER_H

#include "Layer.h"
#include <math.h>

class SigmMSE: public Layer
{
 public:
  SigmMSE(string name_,uint size_,real lr_,real dc_):Layer(name_,size_,lr_,dc_){classname="SigmMSE";};
  SigmMSE(Layer *from,uint start,uint size):Layer(from,start,size){};
  virtual void apply()
    {Layer::apply();real *pon=p;real *po=p;for(uint i=0;i<n;i++)*po++=(real)(1/(1+exp(-(*pon++))));};
  virtual void ComputeOutputSensitivity()
    {real *ps=sensitivity;real *po=this->p;real* pt=targs;for(uint i=0;i<n;i++)*ps++=((*po)-(*pt++))*((*po)*(1-*po++));};
  virtual void multiplyByDerivative()
    {real *ps=sensitivity;real *po=this->p;for(uint i=0;i<n;i++)(*ps++)*=(*po)*(1-*po++);}
  virtual real computeCost(real target);
  virtual ~SigmMSE(){};
};
class TanhMSE: public Layer
{
 public:
  TanhMSE(string name_,uint size_,real lr_,real dc_):Layer(name_,size_,lr_,dc_){setMinMax(-1,1);classname="TanhMSE";};
  TanhMSE(Layer *from,uint start,uint size):Layer(from,start,size){};
  virtual void apply()
    {Layer::apply();real *pon=p;real *po=p;for(uint i=0;i<n;i++)*po++=(real)tanh(*pon++);};
  virtual void ComputeOutputSensitivity()
    {real *ps=sensitivity;real *po=this->p;real* pt=targs;for(uint i=0;i<n;i++)*ps++=((*po)-(*pt++))*(1-(*po)*(*po++));};
  virtual void multiplyByDerivative()
    {real *ps=sensitivity;real *po=this->p;for(uint i=0;i<n;i++)(*ps++)*=1-(*po)*(*po++);};
  virtual ~TanhMSE(){};
};
/// f(x)=tanh(x)+a*x;see tricks of the trade
class TanhMSE2: public Layer
{
 public:
  real a;
  TanhMSE2(string name_,uint size_,real lr_,real dc_,real a_=0.0001):Layer(name_,size_,lr_,dc_){setMinMax(-1,1);classname="TanhMSE2";a=a_;};
  TanhMSE2(Layer *from,uint start,uint size):Layer(from,start,size){};
  virtual void apply()
    {Layer::apply();real *pon=this->p;real *po=p;for(uint i=0;i<n;i++)*po++=(real)tanh(*pon)+a*(*pon++);};
  virtual void ComputeOutputSensitivity()
    {real *ps=sensitivity;real *po=this->p;real* pt=targs;for(uint i=0;i<n;i++)*ps++=((*po)-(*pt++))*(1-(*po)*(*po++))+a;};
  virtual void multiplyByDerivative()
    {real *ps=sensitivity;real *po=this->p;for(uint i=0;i<n;i++)(*ps++)*=1-(*po)*(*po++)+a;};
  virtual ~TanhMSE2(){};
};
/// non satutation Tanh;see tricks of the trade p 18
class NonSatTanhMSE: public Layer
{
 public:
  NonSatTanhMSE(string name_,uint size_,real lr_,real dc_):Layer(name_,size_,lr_,dc_){setMinMax(-1,1);classname="NonSatTanhMSE";};
  NonSatTanhMSE(Layer *from,uint start,uint size):Layer(from,start,size){};
  virtual void apply()
    {Layer::apply();real k=2/3;real *pon=p;real *po=p;for(uint i=0;i<n;i++)*po++=1.7159*(real)tanh(k*(*pon++));};
  virtual void ComputeOutputSensitivity()
    {real *ps=sensitivity;real k=1.7159*(2/3);real *po=this->p;real* pt=targs;for(uint i=0;i<n;i++)*ps++=((*po)-(*pt++))*k*(1-(*po)*(*po++));};
  virtual void multiplyByDerivative()
    {real *ps=sensitivity;real k=1.7159*(2/3);real *po=this->p;for(uint i=0;i<n;i++)(*ps++)*=k*(1-(*po)*(*po++));};
  virtual ~NonSatTanhMSE(){};
};
class LogSoftMax: public Layer
{
 public:
  LogSoftMax(string name_,uint size_,real lr_,real dc_):Layer(name_,size_,lr_,dc_){classname="LogSoftMax";};
  LogSoftMax(Layer *from,uint start,uint size):Layer(from,start,size){};
  virtual void apply();
  virtual void ComputeOutputSensitivity()
    {real *ps=sensitivity;real *po=this->p;real* pt=targs;for(uint i=0;i<n;i++)*ps++=exp(*po++)-*pt++;};
  virtual void multiplyByDerivative()
    {real *ps=sensitivity;real *po=p;for(uint i=0;i<n;i++)(*ps++)*=(1/(*po++));};
  virtual real computeCost(real target);
};
class Linear: public Layer
{
 public:
  Linear(string name_,uint size_,real lr_,real dc_):Layer(name_,size_,lr_,dc_){classname="Linear";};
  Linear(Layer *from,uint start,uint size):Layer(from,start,size){};
  virtual void ComputeOutputSensitivity()
    {real *ps=sensitivity;real *po=p;real* pt=targs;for(uint i=0;i<n;i++)*ps++=(*po++)-(*pt++);};
};
/// Input.p pointer is variable and should point into DataSet
class Input: public Layer
{
 public:
  Input(string name_,uint size_,real lr_,real dc_):Layer(name_,size_,lr_,dc_){classname="Input";free(p);free(targs);do_bprop=false;};
  Input(Layer *from,uint start,uint size):Layer(from,start,size){};
  virtual void apply(){};//nothing to do
  virtual void ComputeOutputSensitivity(){}
  virtual void multiplyByDerivative(){}
  virtual real computeCost(real target){return ((real)0);};
  virtual ~Input(){};
};

Layer* LayerFactory(string con_name,string name,uint size_,real lr_,real dc_);
Layer* FromLayerFactory(string con_name,Layer* from,uint start,uint size);
ostream& operator<<(ostream& out,Layer& layer);
#endif
