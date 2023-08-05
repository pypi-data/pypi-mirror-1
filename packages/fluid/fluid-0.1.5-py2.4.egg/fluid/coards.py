"""Convert COARDS time specification to a datetime object.

This function converts a given COARDS time specification to a Python
datetime object, which is much more useful. Suppose you have an
Array of values [1,2,3] and units "days since 1998-03-01 12:00:00":

    >>> print a
    [1, 2, 3]
    >>> print units
    days since 1998-03-01 12:00:00
    >>> b = [coards.parseUdunits(value, units) for value in a]
    >>> print b[0].year
    1998
    >>> b[1] > b[0]
    True
    >>> print b[1] - b[0]
    1 day, 0:00:00

The list 'b' now contains objects which can be compared and 
manipulated in a consistent way.
"""

__version__ = "$Revision: 6 $"
# $Source$

import re
import datetime


class FixedOffset(datetime.tzinfo):
    """Fixed offset in minutes east from UTC.
    
    This is just a stub Timezone with fixed offset.
    """

    def __init__(self, offset, name):
        self.__offset = datetime.timedelta(minutes=offset)
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return datetime.timedelta(0)


def parseDateString(origin):
    """Parses a date string and returns a datetime object.

    This function parses the 'origin' part of the time unit. It should be
    something like:

        2004-11-03 14:42:27.0 +2:00

    Lots of things are optional; just the date is mandatory.
    """
    # yyyy-mm-dd [hh:mm:ss[.s][ [+-]hh[:][mm]]]
    p = re.compile( r'''(?P<year>\d{4})             # yyyy
                        -                           #
                        (?P<month>\d{1,2})          # mm or m
                        -                           #
                        (?P<day>\d{1,2})            # dd or d
                                                    #
                        (?:                         # [optional time and timezone]
                            \s                      #
                            (?P<hour>\d{1,2})       #   hh or h
                            :                       #
                            (?P<min>\d{1,2})        #   mm or m
                            :                       #
                            (?P<sec>\d{1,2})        #   ss or s
                                                    #
                            (?:                     #   [optional decisecond]
                                \.                  #       .
                                (?P<dsec>\d)        #       s
                            )?                      #
                            (?:                     #   [optional timezone]
                                \s                  #
                                (?P<ho>[+-]?        #       [+ or -]
                                \d{1,2})            #       hh or h
                                :?                  #       [:]
                                (?P<mo>\d{2})?      #       [mm]
                            )?                      #
                        )?                          #
                        $                           # EOL
                    ''', re.VERBOSE)

    m = p.match(origin.strip())
    if m:
        c = m.groupdict(0)
        
        # Instantiate timezone object.
        offset = int(c['ho'])*60 + int(c['mo'])
        tz = FixedOffset(offset, 'Unknown')

        return datetime.datetime(int(c['year']),
                                 int(c['month']),
                                 int(c['day']),
                                 int(c['hour']),
                                 int(c['min']),
                                 int(c['sec']),
                                 int(c['dsec']) * 100000,
                                 tz)
    
    raise Exception, 'Invalid date origin: %s' % origin


def parseUnits(unit):
    """Parse units.

    This function transforms all Udunits defined time units, returning it
    converted to seconds.
    """
    udunits = [(1,                      ['second', 'seconds', 'sec', 's']),
               (60,                     ['minute', 'minutes', 'min']),
               (3.6e3,                  ['hour', 'hours', 'hr', 'h']),
               (8.64e4,                 ['day', 'days', 'd']),
               (1e-8,                   ['shake', 'shakes']),
               (8.616409e4,             ['sidereal_day', 'sidereal_days']),
               (3.590170e3,             ['sidereal_hour', 'sidereal_hours']),
               (5.983617e1,             ['sidereal_minute', 'sidereal_minutes']),
               (0.9972696,              ['sidereal_second', 'sidereal_seconds']),
               (3.155815e7,             ['sidereal_year', 'sidereal_years']),
               (3.15569259747e7,        ['tropical_year', 'tropical_years', 'year', 'years', 'yr', 'a']),
               (29.530589 * 8.64e4,     ['lunar_month', 'lunar_months']),
               (365 * 8.64e4,           ['common_year', 'common_years']),
               (366 * 8.64e4,           ['leap_year', 'leap_years']),
               (365.25 * 8.64e4,        ['julian_year', 'julian_years']),
               (365.2425 * 8.64e4,      ['gregorian_year', 'gregorian_years']),
               (27.321661 * 8.64e4,     ['sidereal_month', 'sidereal_months']),
               (27.321582 * 8.64e4,     ['tropical_month', 'tropical_months']),
               (14 * 8.64e4,            ['fortnight', 'fortnights']),
               (7 * 8.64e4,             ['week', 'weeks']),
               (0.01,                   ['jiffy', 'jiffies']),
               (1e9 * 3.15569259747e7,  ['eon', 'eons']),
               (3.15569259747e7/12,     ['month', 'months']),
              ]
    
    for seconds, units in udunits:
        if unit in units: return seconds

    raise Exception, 'Invalid date unit: %s' % unit


def parseUdunits(value, s):
    """Convert time specification to datetime object.

    This function converts a time specification defined by a value and a 
    unit, returning a datetime object from the Python native module of the
    same name.
    """
    s = s.lower()
    try:
        parts = s.split(' since ')
        unit = parts[0]
        origin = parts[1]
    except:
        raise Exception, 'Invalid date string: %s' % s

    # Convert origin to datetime object.
    origin = parseDateString(origin)

    # Convert unit to seconds.
    unit = parseUnits(unit)
    offset = value * unit

    return origin + datetime.timedelta(seconds=offset)


if __name__ == '__main__':
    print parseUdunits(26, 'Julian_year since 1978-03-09 01:30:00.5 -300')
    print parseUdunits(26, 'Julian_year since 1978-03-09 01:30:00.5 -3')
    print parseUdunits(26, 'Julian_year since 1978-03-09 01:30:00.5 -3:00')
    print parseUdunits(26, 'Julian_year since 1978-03-09 01:30:00.5 -03:00')
    print parseUdunits(26, 'Julian_year since 1978-03-09 01:30:00')
