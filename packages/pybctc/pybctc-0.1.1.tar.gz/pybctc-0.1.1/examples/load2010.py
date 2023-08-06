#~ pybctc is a python package that makes access to the British Columbia
#~ [Canada] Transmission Corporation (BCTC) electric data easier.

#~ Copyright (C) 2010 Keegan Callin

#~ This program is free software: you can redistribute it and/or modify
#~ it under the terms of the GNU General Public License as published by
#~ the Free Software Foundation, either version 3 of the License, or
#~ (at your option) any later version.

#~ This program is distributed in the hope that it will be useful,
#~ but WITHOUT ANY WARRANTY; without even the implied warranty of
#~ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#~ GNU General Public License for more details.

#~ You should have received a copy of the GNU General Public License
#~ along with this program.  If not, see
#~ <http://www.gnu.org/licenses/gpl-3.0.html>.

# Standard library imports
import sys
from datetime import datetime

# 3rd Party Libraries
import pytz
from bctc import BC_TZ
from bctc.load import yield_load_points

def  main():
    start_dt = pytz.utc.localize(datetime(2010, 1, 1))
    end_dt = pytz.utc.localize(datetime(2011, 1, 1))

    print '''2010 BCTC Control Area Load Points'''
    print 'Date, Load'
    for p in yield_load_points(start_dt, end_dt):
        # Time calculations are easier when done in UTC so that no timezone
        # conversions or daylist-savings time conversions need to be made.  For
        # this reason all times yielded by pyaeso are UTC.
        #
        # UTC times are converted to local times when they are displayed to the
        # user.
        print p.t.astimezone(BC_TZ), str(p.load) +'MW'

    return(0)


if __name__ == '__main__':
    sys.exit(main())
