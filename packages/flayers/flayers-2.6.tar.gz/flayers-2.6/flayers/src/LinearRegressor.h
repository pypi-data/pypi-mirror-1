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

#ifndef LINREG
#define LINREG
#include "fLayersGeneral.h"
/// Linear Regressor Class
class LinearRegressor
{
public:
  real X;
  ///sum of x
  real Ex;
  ///mean of x
  real Mx;
  real SSx;
  real Ey; 
  real My;
  real SPxy;
  uint n;
  LinearRegressor(){X=0;Ex=0;Mx=0;SSx=0;Ey=0;My=0;SPxy=0;};
  void init(uint n_history,real extrapolation_factor);
  void linearRegression(real **history,uint i,real* weights);
};
#endif
