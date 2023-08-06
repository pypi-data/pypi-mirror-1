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

#include "Weights.h"
#include "math_util.h"

Weights::Weights(string name_,uint size,real lr_,real dc_)
{
  name=name_;n=size;lr=lr_;start_lr=lr_;dc=dc_;
  w=realMalloc(n);
  wu=realMalloc(n);
  do_bprop=true;do_fprop=true;
}
void Weights::randomInit(real max)
{
	real *p=w;
	for(uint i=0;i<n;i++)
		*p++=randomu(max);
}
void Weights::perturb(real fraction,bool extremum)
{
  real* p=w;
  for(uint i=0;i<n;i++){
      if(extremum){
	if (randomu(1)>0)
	  (*p)+=fraction*(*p++);
	else
	  (*p)-=fraction*(*p++);
      }else
	(*p)+=randomu(fraction*(*p++)); 
    p++;
  }
}  
ostream& operator<<(ostream& out,Weights& w)
{
	out<<"\nWeights :"<<endl;
	printVecReal(w.w,w.n,false,10,&out);return out;
}
LrWeights::LrWeights(string name_,uint size,real lr_,real dc_):Weights(name_,size,lr_,dc_)
{
  inc_factor=1.1f;dec_factor=0.7f;
  old_weights_updates=realMalloc(n);
  old_weights=realMalloc(n);
  lrs=realMalloc(n);
   //set all lr to 1
  set(lrs,n,lr*inc_factor);//at first iteration, all lrs will be reduce
}
void LrWeights::updateParamsLr()
{
	real *plr=lrs;
	real *owu=old_weights_updates;//old weights update
	real *cwu=wu;//courant weights update 
    for(uint i=0;i<n;i++){
		if( ((owu[i]>0)&&(cwu[i]>0)) || ((owu[i]<0)&&(cwu[i]<0)) )
			plr[i]*=inc_factor;
		else
			plr[i]*=dec_factor;
	}
	//printVecReal(lrs,n);
}
void LrWeights::initEpoch(int i)
{
	if(i==1)memcpy(old_weights,w,n*sizeof(real));
	//compute new gradient
	real *pwu=wu; 
    real *pw=w;
	real *pow=old_weights;
    for(uint j=0;j<n;j++)
		*pwu++=(*pw++)-(*pow++);
	//clear all gradient with hack to memory cpy optimisation
	real* temp_old_weights_updates=old_weights_updates;
    old_weights_updates=wu;
    wu=temp_old_weights_updates;
    memset(wu,0,n*sizeof(real));
	//update learning rates
	updateParamsLr();
	memcpy(old_weights,w,n*sizeof(real));
}
LrWeights::~LrWeights()
{
	free(old_weights);
	free(old_weights_updates);
	free(lrs);
	lrs=NULL;old_weights_updates=NULL;old_weights=NULL;
}

