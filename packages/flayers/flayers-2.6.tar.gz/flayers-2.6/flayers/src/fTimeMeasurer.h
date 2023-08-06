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

#ifndef TIMEMEASURER
#define TIMEMEASURER

#include "fLayersGeneral.h"
#ifdef WIN32
#include <time.h>
#define CLK CLK_TCK
#define FACTOR_CLK 1000
#endif
#ifndef WIN32
#include <sys/times.h>
#define CLK CLOCKS_PER_SEC
#define FACTOR_CLK 10000
#endif
///
///  \class fTimeMeasurer fTimeMeasurer.h "Utils/fTimeMeasurer.h" 
///  \brief fTimeMeasurer class do all related to time measurement.
///
/// -why ? : need experimentation time measurement.
/// author : Francis Pieraut and J-S Senecal
///
class fTimeMeasurer
{
 protected:
  bool started;
    time_t t_before,t_after;
    long cpu_t_before, cpu_t_after;
 public:
   static long getRuntime();
    fTimeMeasurer()
      {t_before=0;t_after=0;started=false;};
	/// Restarts the timer and return current time
    string startTimer(bool with_host=false);
	/// Stop the timer and returns current time
    string stopTimer(bool cpu_time=false);
    /// Restart the timer, but keep in memory the last running time i.e. difference between time at startTimer (or resumeTimer) and last call
    /// to stopTimer (or getStopRunningTime); returns current time
    string getRunningTime(bool only_time=true, bool cpu_time=true);// Returns the running time between start and stop
    string getStopRunningTime(bool only_time=true, bool cpu_time=true);// Stops and returns the running time between start and stop (i.e. now)
    double getStopTime();
};

#endif
