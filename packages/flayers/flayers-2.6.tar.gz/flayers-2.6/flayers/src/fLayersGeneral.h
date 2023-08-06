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

#ifndef FGENERAL_H
#define FGENERAL_H

#include <fstream>
#include <string>
#include <iostream>
#include <list>
using namespace std;
#include <stdlib.h>
#include <memory.h>
#include <math.h>
#include "fTimeMeasurer.h"
#include "limits.h"
#include "float.h"

//#ifdef WIN32
//#define FLT_MAX _I16_MAX
//#endif
//typedef float real;
#ifndef real
typedef float real;
#endif
//typedef double real;
//#define real float
#define uint unsigned int

class fError { public: fError(const string &m) : msg(m) {}; string msg; };
void FERR(string msg);

//#define MISSING_VALUE -999
void printVecReal(real* r,uint size,bool return_line=true,int setw_size=10,ostream *out=NULL);
void readVecReal(real* r,uint size,istream *in);
real* realCalloc(uint nelems,uint size);
real* realMalloc(uint nelems);
uint* uintCalloc(uint nelems,uint size);
uint* uintMalloc(uint nelems);
void realDiv(real* r,uint size,real div);
void realPow(real* r,uint size,real base);
string tostring(double x);
void set(real* r,uint size,real value);
string troncString(string name);
string argvToString(int argc, char* argv[]);
string argvToString(char* argv[],char* stop);
char** stringToArgv(string cmd,int &size);
void freeStringToArgv(char** tab,int size);
real realAbs(real r);
#endif
