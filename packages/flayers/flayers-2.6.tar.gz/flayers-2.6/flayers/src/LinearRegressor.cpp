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

#include "LinearRegressor.h"
void LinearRegressor::init(uint n_history,real extrapolation_factor)
{
  X=extrapolation_factor;
  cout<<"Create a linear regressor; x= "<<X<<endl;
  Ex=0;//sum of x
  Mx=0;//mean of x
  SSx=0;
  Ey=0; 
  My=0;
  SPxy=0;
  uint n=n_history;
  uint x=0;
  //compute sum of x 
  for(x=0;x<n;x++)
    Ex+=x;
  // compute mean x
  Mx=Ex/n;
  //compute SSX 
  for(x=0;x<n;x++)
    SSx+=(x-Mx)*(x-Mx);
}
/// regression linear with n points y=mx+b
/// m=SPxy/SSx
/// b=My-m*Mx
void LinearRegressor::linearRegression(real **history,uint i,real* weights)
{
  real m,b;
  uint x=0;
  Ey=0;My=0;
  for(x=0;x<n;x++){
    Ey+=history[x][i];
    My=Ey/n;
  }
  for(x=0;x<n;x++){
    SPxy=(x-Mx)*(history[x][i]-My);
  }
  m=SPxy/SSx;
  b=My-m*Mx;
  weights[i]=m*X+b;
}
