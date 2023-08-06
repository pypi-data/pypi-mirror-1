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

#ifndef ARGVPARSERCONTAINER
#define ARGVPARSERCONTAINER

#include "ArgvParser.h"
typedef list<ArgvParser*>::const_iterator ARGV_LI;
///
///  \class ArgvParserContainer ArgvParserContainer.h "Utils/ArgvParserContainer.h"
///  \brief ArgvParserContainer is a container of ArgvParser.
///
class ArgvParserContainer
{
 protected:
  list<ArgvParser*> parsers_;
  string progname_;
 public:
  ArgvParserContainer(string progname="Program"){progname_=troncString(progname);};
  void add(ArgvParser* parser){parsers_.push_back(parser);};
  void usage();
  void parse(int &argc,char *argv[]);
  string getStringDescriptor(bool short_descr=true,ofstream *output=NULL);
  void updateCmdLine();
  string getCmdLine(bool short_rep=true);
  ArgvParser* getArgvParser(string name){ArgvParser* ap=getArgvParserOrNull(name);if(ap==NULL){FERR(name+" is not include in  ArgvParserContainer");return NULL;}else return ap;};
  ///WARNING if not found, return NULL
  ArgvParser* getArgvParserOrNull(string name);
};
#endif
