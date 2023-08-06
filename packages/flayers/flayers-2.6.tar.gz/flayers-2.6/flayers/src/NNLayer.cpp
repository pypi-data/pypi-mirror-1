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

#include "NNLayer.h"

Layer* LayerFactory(string con_name,string name,uint size,real lr,real dc)
{
  if(con_name=="SigmMSE")
    return new SigmMSE(name,size,lr,dc);
  else if(con_name=="TanhMSE")
    return new TanhMSE(name,size,lr,dc);
  else if(con_name=="TanhMSE2")
    return new TanhMSE2(name,size,lr,dc);
  else if(con_name=="NonSatTanhMSE")
    return new NonSatTanhMSE(name,size,lr,dc);
  else if(con_name=="LogSoftMax")
    return new LogSoftMax(name,size,lr,dc);
  else if(con_name=="Linear")
    return new Linear(name,size,lr,dc);
  else if(con_name=="Input")
    return new Input(name,size,lr,dc); 
  else FERR(("undefine Active Function ->"+con_name).c_str());
  return 0;
}
Layer* FromLayerFactory(string con_name,Layer* from,uint start,uint size)
{
  if(con_name=="SigmMSE")
    return new SigmMSE(from,start,size);
  else if(con_name=="TanhMSE")
    return new TanhMSE(from,start,size);
  else if(con_name=="TanhMSE2")
    return new TanhMSE2(from,start,size);
  else if(con_name=="NonSatTanhMSE")
    return new NonSatTanhMSE(from,start,size);
  else if(con_name=="LogSoftMax")
    return new LogSoftMax(from,start,size);
  else if(con_name=="Linear")
    return new Linear(from,start,size);
  else if(con_name=="Input")
    return new Input(from,start,size); 
  else FERR(("undefine Active Function ->"+con_name).c_str());
  return 0;
}
real SigmMSE::computeCost(real target)
{
  real *ptarg=targs;
  real *pout=p; 
  uint i;
  real out_targ=0; //output-target
  //set target
  if(n>1)
    targs[(int)target]=max_targ;
  else targs[0]=target;
  // pow((ouputs-targets),2)
  for(i=0;i<n;i++)
    out_targ+=(*pout-*ptarg)*(*pout++ - *ptarg++);
  // unset classification target
  if(n>1)
    targs[(int)target]=min_targ;
  return out_targ;
}
void LogSoftMax::apply()
{
  Layer::apply();
  uint i;
  real *po=p;
  real *pon=p;
  // find max
  real max=*pon;//default first position
  for(i=0;i<n;i++,pon++){
    if (*pon>max){max=*pon;};
  } 
  pon=p;
  real sum=0;po=p;
  //exp + sum
  for(i=0;i<n;i++){
    *po=*pon++ - max; 
    sum+=exp(*po++);
  }
  po=p;
  //xi-log(sum) 
  real logsum=log(sum);
  for(i=0;i<n;i++,po++)*po=*po-logsum;
}
real LogSoftMax::computeCost(real target)
{  
  real *ptarg=targs;
  real *pout=p; 
  uint i;real nll=0;//negativ log likelyhood 
  //set target
  if(n>1)
    targs[(int)target]=max_targ;
  else targs[0]=target;
  for(i=0;i<n;i++)
    //nll-=(*ptarg)*exp(-*pout)+(1-*ptarg++)*exp(1-*pout++);//real cost ***
    nll-=(*ptarg)*(-*pout)+(1-*ptarg++)*(1-*pout++);//simplification estimation to avoid float overflow
  // unset classification target
  if(n>1)
    targs[(int)target]=min_targ;
  return (nll);
}


