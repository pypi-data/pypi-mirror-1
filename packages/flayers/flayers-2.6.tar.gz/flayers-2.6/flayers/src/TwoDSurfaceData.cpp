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

#include "TwoDSurfaceData.h"
void TwoDSurfaceData::parse(int argc,char* argv[])
{
  ArgvParser::parse(argc,argv);
  createData();
  if(getBool("normalize"))
    normalizeDataInputs();//printData();
  if(getInt("n_classes")==1)
    cout<<"WARNING: are we in regression mode? if yes then --regression 1"<<endl;
  if((getInt("n_classes")==1)&&getBool("regression"))
    normalizeTarget(); 
  if((getInt("n_classes")!=1)&&getBool("regression"))
    FERR("can't be in regression mode if n_classes=1");
  // reduce matrice dim for test
  real fraction_input=getReal("fraction_input");
  if ((fraction_input<1)&&(fraction_input>0)){
    FERR("reduce inputs size not implemented");
  }
  set("do_shuffle","0");//IMPORTANT we don't want shuffling
  // split data in train_set,valid_set and train_set
  splitTrainValidTest(); 
} 
void TwoDSurfaceData::createData()
{
  uint d=getInt('D');
  set("n_inputs",2);
  set("n_examples",d*d);
  real max_x=getReal("max_x");
  real max_y=getReal("max_y");
  // alloc data_ and targets_
  data_=realCalloc(2*d,d);
  targets_=realMalloc(d);
  // init data
  real *pdata=data_;
  cout<<"Createdata :"<<d<<"X"<<d<<endl;
  for(uint y=d;y>0;y--)
    for(uint x=1;x<(d+1);x++){
      *pdata++=(x/(real)d)*max_x;
      *pdata++=(y/(real)d)*max_y;
    }
  //printData();
}
void TwoDSurfaceData::normalizeDataInputs()
{
  if (dsp){
    cout<<"Normalisation with train mean and variance"<<endl;
    //normalize data
    real *pdata=data_;
    real *pmean=dsp->means;
    real *pvar=dsp->vars;
    for(uint i=0;i<n*n;i++,pmean=dsp->means,pvar=dsp->vars){
      for(uint j=0;j<n;j++){
        //remove mean
        *pdata=*pdata-*pmean++;
        //divide by variance if !=0
        if(*pvar)
          *pdata++ /=*pvar++;
        else{
          *pvar++;*pdata++;
        }
      }
    }
  }else{
    DataSetArgvParser::normalizeDataInputs();
    cout<<"Normalise with 2dsurface mean and variance"<<endl;
  }
}

