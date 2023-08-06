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

#include "fDataSet.h"

int Random(real n){return (int)(n*(double(rand())/RAND_MAX));}
void RandomDataSet::initTable()
{
  // init attributs
  table_=(uint*)malloc(size_*sizeof(uint));
  //init table
  for (uint j=0;j<size_;j++)
    table_[j]=j;
  //shuffle table
  int r;//random number
  uint tampon;
  for (uint i=0;i<(size_-1);i++){
    r=Random(size_-i-1)+i;
    tampon=table_[i];
    table_[i]=table_[r];
    table_[r]=tampon;
  }
  if (size_<=20)printTable();
  //init DataSet attributs
}
void RandomDataSet::printTable()
{
  cout<<"RandomData table, size="<<size_<<endl;
  for (uint i=0;i<size_;i++)
    cout<<i<<" "<<table_[i]<<endl;
}
DataSet* SeqDataSet::getSubSet(uint start,uint size,uint iter_size)
{
  if ( (start>size_) || ((start+size)>size_) ){
    FERR("Error in getSetSet(...)");
    return NULL;
  }
  return new SeqDataSet(data_+(start*input_size_),targs_+start,size,iter_size,input_size_,max_input_size_,true);
}
DataSet* RandomDataSet::getSubSet(uint start,uint size,uint iter_size)
{
  if ( (start>size_) || ((start+size)>size_) ){
    FERR("Error in getSetSet(...)");
    return NULL;
  }
  RandomDataSet * rds=new RandomDataSet(data_,targs_,size,iter_size,input_size_,max_input_size_,true);
  rds->table_=table_+start;
  return rds;
}
ostream& operator<<(ostream& out,DataSet& ds)
{
	cout<<"DataSet :"<<endl;
	for(uint z=0;z<ds.size_;z++){
		cout<<ds.input_<<" ";
		printVecReal(ds.input_,ds.input_size_);
		ds.next();
	}
	return out;
}
