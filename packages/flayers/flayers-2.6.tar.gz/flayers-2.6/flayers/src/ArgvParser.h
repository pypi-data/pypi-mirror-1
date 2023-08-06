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

#ifndef ARGVPARSER
#define ARGVPARSER
#include "fLayersGeneral.h"
///
/// ArgvParser/PreDefArgvParser/ArgvParserContainer 
/// -why ? : main idea :    
///          Need simple and easy to use command line arguments parsing.
///          (Need something better then getopt.h)
/// specifics needs:
///          Need reusable parsing components.
///          Need automatic experiment name generator related to parameters.
///          Need automatic usage generator.
///          Need easy default values setting.
///          Need easy interface to get back arguments values.(getBool('c'),getReal("n_epochs") etc.)
///          Need simple automatic coherence parameters checker. 
///          Need simple arguments type setting (int,char,real...).
///  
/// Author : Francis Pieraut   
/// examples: /u/pierautf/fLayers/fLayersLib/Examples/SimpleArgvParser.cpp
///           /u/pierautf/fLayers/fLayersLib/Examples/SimpleArgvParser2.cpp
///           /u/pierautf/fLayers/fLayersLib/Examples/SimpleArgvParserContainer.cpp
///          /u/pierautf/fLayers/fLayersLib/Examples/fexp.cpp
///
enum argv_type{INT,REAL,STRING,CHAR,BOOL,CASE,NOTDEF};

///
///  \class  opt ArgvParser.h "Utils/ArgvParser.h" 
///  \brief define argument option.
///
/// opts is the most important structure you need to define to use ArgvParser
/// IMPORTANT : if you use opt[], last position = opt('>',"","",""), so call no argv constructor -> opt()
/// WARNING don't use empty string ""->strange things with STL !!
///
class opt
{
  public:
  opt(){c='>';name="";value="";description="";type=NOTDEF;pointer=NULL;};
  opt(char c, string name,string value,string description,argv_type type,void *pointer=NULL)
    {this->c=c;this->name=name;this->value=value;this->description=description;this->type=type;this->pointer=pointer;};
  // short option reference character (ex: -c 1)
  char c;           
   // option name
  string name;      
  // option default value
  string value;      
  // option description
  string description;
   // argument type
  argv_type type;   
   // pointer to the associate parameter
  void* pointer;        
  void setPointer(void *p){pointer=p;};//{cout<<"option->pointer "<<name<<" is set "<<endl;pointer=p;}; 
};
///
///  \class noargopt ArgvParser.h "Utils/ArgvParser.h" 
///  \brief define no argument option.
///
/// this structure is optional and define options with no arguments.
/// IMPORTANT : no argument option need to be define first in "opts_" list
/// IMPORTANT : last position = opt(">","","") so call no argv constructor -> noargopt()
///
class noargopt
{
  public:
  noargopt(){name=">";opt_name="";value="";};
  noargopt(string name,string opt_name,string value)
  {this->name=name;this->opt_name=opt_name;this->value=value;};
  string name;     /// option name, long or short option can be used
  string opt_name; /// this name should be one of the name in shortoptions.name or shortoptions.c
  string value;    /// value to assign if this option is use
};
typedef list<opt>::iterator OPT_LI;
typedef list<noargopt>::iterator NOARGOPT_LI;
class ArgvParser
{
 protected:
  ///list of short options, generate automaticaly in init(..)
  char* shortopts_;    
  ///descrition of ArgvParser 
  string description_; 
  string examples_;
  ///nb of default values modify
  int n_modif;         
  /// options list
  list<opt> opts_;     
  list<noargopt> noargopts_;
  void printOpts();
  void printNoArgOpts();
  void printExamples();
public:
  ///name of ArgvParser
  string name_;        
  ///all options in string representation
  string string_options_;
  ArgvParser(string name="",
	     opt *opts=NULL,
	     noargopt *noargopts=NULL,
	     string description="",
	     string examples="");  
  // Most important functions
  void usage(bool with_presentation=true); 
  virtual void parse(int argc,char* argv[]); 
  /// add options and no argument option
  void addOpt(opt *option);
  void addOpt(char c,string name,string value,string description,argv_type type,void *pointer=NULL){addOpt(new opt(c,name,value,description,type,pointer));};
  void addNoArgOpt(noargopt *option){noargopts_.push_front(*option);};
  void addNoArgOpt(string name,string opt_name,string value){addNoArgOpt(new noargopt(name,opt_name,value));};
  /// set options values
  void set(char key,string s);
  void set(char key,int value){set(key,tostring(value));};
  void set(string key,string s);
  void set(string key,int value){set(key,tostring(value));};
  void set(char* key, char* s){set(string(key),s);};
  /// get options values
  string get(string key,void* p=NULL); 
  char getChar(string key,char* p=NULL);
  real getReal(string key,real* p=NULL);
  int getInt(string key,int* p=NULL);
  bool getBool(string key,bool* p=NULL);
  string get(char key,void* p=NULL);
  char getChar(char key,char* p=NULL);
  real getReal(char key,real* p=NULL);
  int getInt(char key,int* p=NULL);
  bool getBool(char key,bool* p=NULL);
  /// find 
  OPT_LI findOpt(char c);
  OPT_LI findOpt(string s); 
  NOARGOPT_LI findNoArgOpt(string s);
  // others
  string toString(argv_type at);
  void updateCmdLine();
  string getCmdLine(bool short_rep=true);//short representation else long representation (ex: -a or --algo)
  void printDescription();
  virtual string getStringDescriptor(bool short_descr=true,ofstream *output=NULL);
  int getNbdefaultValModify(){return n_modif;};
  string getName(){return name_;};
  void setDescription(string description){description_=description;};
  string getDescription(){return description_;};
  ///this fct is call before and after parse()
  ///if you overwrite it call ArgvParser::CoherenceParamsValuesChecker()
  virtual void CoherenceParamsValuesChecker();
  virtual ~ArgvParser(){free(shortopts_);};
 private:
  bool SetNoArgOpt(string option);
  int getNextOption(int argc,char* argv[]);
  void init(opt* shortopts,noargopt* noargopts);
  void initShortOpts();
};    

#endif
  
