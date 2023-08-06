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

#ifndef TWODSURFACEDATA
#define TWODSURFACEDATA

#include "PreDefArgvParser.h"
///  \class TwoDSurfaceData TwoDSurfaceData.h "Work/TwoDSurfaceData.h" 
///  \brief TwoDSurfaceData represent a 2 Dimentions DataSetArgvParser. 
///
/// generate 2D Surface DataSet of n X n
/// specifiy nb of examples -e or --n_examples
class TwoDSurfaceData:public DataSetArgvParser{
public:
  DataSetArgvParser* dsp;//use to do same normalisation of train_set
  uint n;//data nXn
  TwoDSurfaceData():DataSetArgvParser()
    {addOpt('D',"dim_x_y","6","dimention of surface NXN",INT);
    addOpt('x',"max_x","6","max value of x",REAL);
    addOpt('y',"max_y","6","max value of y",REAL);dsp=NULL;};
  void setDSP(DataSetArgvParser* dsp_){dsp=dsp_;};
  virtual void parse(int argc,char* argv[]);
  void createData();
  void normalizeDataInputs();
};
#endif
