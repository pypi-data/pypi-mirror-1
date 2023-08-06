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

#ifndef WEIGHTSLIST_H
#define WEIGHTSLIST_H

#include "fLayersGeneral.h"
#include "Weights.h"

typedef list<Weights*>::iterator WEIGHTS_LI;
///  \class WeightsList WeightsList.h "Core/WeightsList.h" 
///  \brief WeightsList represent a list of objects Weights. 
class WeightsList
{
 public:
  WeightsList(){size=0;};
  uint size;
  list<Weights*> list_;
  bool set(uint i, real val);//set parameter i to val
  real get(uint i);
  void add(Weights *w);
  real sumAbs();
  real* copyOfAllWeights(real* cpy_to=NULL);
  void copyFrom(real* source);
  void copyFrom(WeightsList *pl);
  void displayNameList();
  void perturb(real fraction,bool extremum=false);
  void cleanup();
  void clearUpdates();
  bool isSame(WeightsList *pl);
  void randomInit(real max);
  void set(real r);
  ~WeightsList(){cleanup();};
};    
ostream& operator<<(ostream& out,WeightsList& pl);
istream& operator>>(istream& in,WeightsList& pl);
#endif
			     

      
  
  
