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

#include "LrConnector.h"

void LrGeneral::memAlloc()
{
  old_weights_updates=realMalloc(n);
  lrs=realMalloc(n);
   //set all lr to 1
  set(lrs,n,lr*inc_factor);//at first iteration, all lrs will be reduce
}
void LrGeneral::memFree()
{
  free(old_weights_updates);free(lrs);
  lrs=NULL;old_weights_updates=NULL;
}
void LrGeneral::updateParamsLr()
{
	real *plr=lrs;
	real *owu=old_weights_updates;//old weights update
	real *cwu=weights_updates;//courant weights update
    for(uint i=0;i<n;i++){
		if( ((owu[i]>0)&&(cwu[i]>0)) || ((owu[i]<0)&&(cwu[i]<0)) )
			plr[i]*=inc_factor;
		else
			plr[i]*=dec_factor;
	}
	//printVecReal(lrs,n);
}
void LrGeneral::initEpoch(int i)
{
	Connector::initEpoch(i);
	//compute new gradient
	real *pwu=weights_updates;
    real *pw=weights;
	real *pow=old_weights;
    for(uint j=0;j<n;j++)
		*pwu++=(*pw++)-(*pow++);
	//clear all gradient with hack to memory cpy optimisation
	real* temp_old_weights_updates=old_weights_updates;
    old_weights_updates=weights_updates;
    weights_updates=temp_old_weights_updates;
    memset(weights_updates,0,outl->n*inl->n*sizeof(real));
	//update learning rates
	updateParamsLr();
}
