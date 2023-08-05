#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob, math, re, traceback, unittest
from datetime import datetime
from time import strptime
import ephem

# Read an ephemeris from the United States Naval Observatory, and
# confirm that PyEphem returns the same measurements to within one
# arcsecond of accuracy.

class Datum(object):
    pass

def interpret_observer(line):
    """Return the Observer represented by a line from a USNO file.
              Location:  W 84°24'36.0", N33°45'36.0",   322m
    """
    line = line.replace('W ', 'W').replace('E ', 'E')
    line = line.replace('N ', 'N').replace('S ', 'S')
    fields = line.split()
    observer = ephem.Observer()
    observer.long = ':'.join(re.findall(r'[0-9.]+', fields[1]))
    observer.lat = ':'.join(re.findall(r'[0-9.]+', fields[2]))
    if fields[1].startswith('W'):
        observer.long *= -1
    if fields[2].startswith('S'):
        observer.lat *= -1
    observer.elevation = float(fields[-1][:-1])
    setup_horizon(observer)
    return observer

def setup_horizon(observer):
    observer.pressure = 0
    observer.horizon = '-0:34'  # per USNO definition

def standard_parse(line):
    """Read the date, RA, and dec from a USNO data file line."""

    fields = re.split(r'   +', line)
    dt = datetime(*strptime(fields[0][:-2], "%Y %b %d %H:%M:%S")[0:6])
    date = ephem.Date(dt)
    ra = ephem.hours(fields[1].replace(' ', ':'))
    sign, mag = fields[2].split(None, 1)
    dec = ephem.degrees(sign + mag.replace(' ', ':'))
    return date, ra, dec

def is_near(n, m, error = ephem.arcsecond):
    """Raise an exception if two values are not within an arcsecond."""

    if abs(n - m) > error:
        raise AssertionError('the USNO asserts the value %s'
                             ' but PyEphem instead returns %s'
                             % (n, m))

class Trial(object):
    def select_body(self, name):
        """Return solar system bodies and stars for USNO computations."""
        if hasattr(ephem, name):
            return getattr(ephem, name)()
        else:
            return ephem.star(name)

    def examine_content(self):
        """Return the object named on the first line of the file.

        Since most USNO files name a heavenly body on their first
        line, this generic examine_content looks for it and sets
        "self.body" accordingly.  If when you subclass Trial you are
        dealing with a file that does not follow this convention, then
        both override examine_content with one of your own, and
        neglect to call this one.

        """
        firstline = self.lines[0]
        name = firstline.strip()
        self.body = self.select_body(name)

    def finish(self):
        """Conclude the test.

        By overriding this function, the author of a Trial can do
        processing at the end of his test run.  Commonly, this is used
        when check_data_line() just stores what it finds in each data
        line, and the results need to be checked as a unit.

        """

    def run(self, content):
        def report_error():
            return RuntimeError(
                'USNO Test file %r raised exception:%s\n'
                % (self.path, traceback.format_exc()))

        self.content = content
        self.lines = content.split('\n')
        self.examine_content()
        for line in self.lines:
            if line.strip() and line[0].isdigit():
                try:
                    self.check_data_line(line)
                except:
                    raise report_error()
        try:
            self.finish()
        except:
            raise report_error()

# Check an "Astrometric Positions" file.

class Astrometric_Trial(Trial):
    @classmethod
    def matches(self, content):
        return 'Astrometric Positions' in content

    def check_data_line(self, line):
        date, ra, dec = standard_parse(line)

        self.body.compute(date)
        is_near(ra, self.body.a_ra)
        is_near(dec, self.body.a_dec)

# Check an "Apparent Geocentric Positions" file.

class Apparent_Geocentric_Trial(Trial):
    @classmethod
    def matches(self, content):
        return 'Apparent Geocentric Positions' in content

    def check_data_line(self, line):
        date, ra, dec = standard_parse(line)

        self.body.compute(date)
        is_near(ra, self.body.g_ra)
        is_near(dec, self.body.g_dec)

        # The values we get should not depend on our epoch.

        self.body.compute(date, epoch=date)
        is_near(ra, self.body.g_ra)
        is_near(dec, self.body.g_dec)

        # Since we only provided the body with a date, and not an
        # Observer, the computation should have been geocentric, and
        # thus the "ra" and "dec" fields should have had the apparent
        # positions copied into them as well.

        assert self.body.g_ra == self.body.ra
        assert self.body.g_dec == self.body.dec

# Check an "Apparent Topocentric Positions" file.

class Apparent_Topocentric_Trial(Trial):
    @classmethod
    def matches(self, content):
        return 'Apparent Topocentric Positions' in content

    def examine_content(self):
        Trial.examine_content(self) # process object name on first line
        for line in self.lines:
            if 'Location:' in line:
                self.observer = interpret_observer(line.strip())

    def check_data_line(self, line):
        date, ra, dec = standard_parse(line)
        self.observer.date = date
        self.body.compute(self.observer)
        is_near(ra, self.body.ra)
        is_near(dec, self.body.dec)

# Check several days of risings, settings, and transits.

class Rise_Transit_Set_Trial(Trial):
    def __init__(self):
        self.data = []

    @classmethod
    def matches(self, content):
        return 'Rise  Az.       Transit Alt.       Set  Az.' in content

    def examine_content(self):
        Trial.examine_content(self) # process object name on first line
        for line in self.lines:
            if 'Location:' in line:
                self.observer = interpret_observer(line.strip())
            elif 'Time Zone:' in line:
                if 'west of Greenwich' in line:
                    self.tz = - int(line.split()[2].strip('h')) * ephem.hour

    def check_data_line(self, line):
        """Determine if our rise/transit/set data match the USNO's.

The file looks something like:
      Date               Rise  Az.       Transit Alt.       Set  Az.
     (Zone)
                          h  m   °         h  m  °          h  m   °
2006 Apr 29 (Sat)        10:11 100        15:45 42S        21:19 260
2006 Apr 30 (Sun)        10:07 100        15:41 42S        21:15 260
2006 May 01 (Mon)        10:03 100        15:37 42S        21:11 260

        Here we save the data in self.data for examination by finish().
        """
        datum = Datum()
        fields = line.split()

        dt = datetime(*strptime(' '.join(fields[0:3]), "%Y %b %d")[0:3])
        midnight = ephem.Date(ephem.Date(dt) - self.tz)
        datum.midnight = midnight

        def parse(fields, n):
            if len(fields) < n + 2:
                return None, None
            (timestr, anglestr) = fields[n:n+2]
            if timestr == '*****':
                return None, None
            h, m = [ int(s) for s in timestr.split(':') ]
            date = ephem.Date(midnight + h * ephem.hour + m * ephem.minute)
            angle = ephem.degrees(anglestr.strip('NS'))
            return date, angle

        datum.rising, datum.rising_az = parse(fields, 4)
        datum.transit, datum.transit_alt = parse(fields, 6)
        datum.setting, datum.setting_az = parse(fields, 8)

        self.data.append(datum)

    def finish(self):
        """Go back through and verify the data we have saved."""

        observer = self.observer
        body = self.body
        data = self.data

        # This helper function, given an attribute name of
        # "rising", "transit", or "setting", verifies that the
        # observer and body are locate at the time and place that
        # the named transit attributes say they should be.

        def check(attr):
            is_near(getattr(datum, attr), observer.date, ephem.minute)
            if attr == 'transit':
                datum_angle = datum.transit_alt
                our_angle = body.alt
            else:
                datum_angle = getattr(datum, attr + '_az')
                our_angle = body.az
            is_near(datum_angle, our_angle, ephem.degree)

        # Make sure that, from both the midnight starting the day and
        # the midnight ending the day, we can move to the events that
        # happen during each day.

        for i in range(len(data)):
            datum = data[i]

            for attr in ('rising', 'transit', 'setting'):
                datum_date = getattr(datum, attr)

                if datum_date is not None:
                    observer.date = datum.midnight
                    getattr(observer, 'next_' + attr)(body)
                    check(attr)

                    observer.date = datum.midnight + 1
                    getattr(observer, 'previous_' + attr)(body)
                    check(attr)

        # Make sure we can also jump along similar events.

        for attr in ('rising', 'transit', 'setting'):
            prev = None
            for i in range(len(data)):
                datum = data[i]
                datum_date = getattr(datum, attr)
                if datum_date is None:
                    prev = None
                else:
                    if prev is None:
                        observer.date = datum.midnight
                    getattr(observer, 'next_' + attr)(body)
                    check(attr)
                    prev = observer.date

        for attr in ('rising', 'transit', 'setting'):
            next = None
            for i in range(len(data) - 1, 0, -1):
                datum = data[i]
                datum_date = getattr(datum, attr)
                if datum_date is None:
                    next = None
                else:
                    if next is None:
                        observer.date = datum.midnight + 1
                    getattr(observer, 'previous_' + attr)(body)
                    check(attr)
                    next = observer.date

# Check a whole year of "Rise and Set for the * for *" file.

class Rise_Set_Trial(Trial):
    @classmethod
    def matches(self, content):
        return 'Rise and Set for' in content

    def examine_content(self):
        name, year = re.search(r'Rise and Set for (.*) for (\d+)',
                               self.content).groups()
        if name.startswith('the '):
            name = name[4:]
        self.body = self.select_body(name)
        self.year = int(year)

        longstr, latstr = re.search(r'Location: (.\d\d\d \d\d), (.\d\d \d\d)',
                                    self.content).groups()
        longstr = longstr.replace(' ', ':').replace('W', '-').strip('E')
        latstr = latstr.replace(' ', ':').replace('S', '-').strip('N')

        self.observer = o = ephem.Observer()
        o.lat = latstr
        o.long = longstr
        o.elevation = 0
        setup_horizon(o)

        self.error = ephem.minute # error we tolerate in predicted time

    def check_data_line(self, line):
        """Determine whether PyEphem rising times match those of the USNO.
        Lines from this data file look like:

               Jan.       Feb.       Mar.       Apr.       May    ...
        Day Rise  Set  Rise  Set  Rise  Set  Rise  Set  Rise  Set ...
             h m  h m   h m  h m   h m  h m   h m  h m   h m  h m ...
        01  0743 1740  0734 1808  0707 1834  0626 1858  0549 1921 ...
        02  0743 1741  0734 1809  0705 1835  0624 1859  0548 1922 ...

        Note that times in this kind of file are in Eastern Standard
        Time, so we have to variously add and subtract fives hours
        from our UT times to perform a valid comparison.
        """

        def two_digit_compare(event, usno_digits):
            usno_hrmin = usno_digits[:2] + ':' + usno_digits[2:]
            usno_date = ephem.Date('%s %s' % (usno_datestr, usno_hrmin))

            difference = o.date - (usno_date + 5 * ephem.hour)
            if abs(difference) > self.error:
                raise ValueError('On %s, the USNO thinks that %s %s'
                                 ' happens at %r but PyEphem finds %s'
                                 % (usno_datestr, body.name, event,
                                    usno_hrmin, o.date))

        o = self.observer
        year = self.year
        body = self.body
        day = int(line[0:2])
        for month in [ int(m) for m in range(1,13) ]:
            usno_datestr = '%s/%s/%s' % (year, month, day)

            offset = month * 11 - 7 # where month is in line
            usno_rise = line[offset : offset + 4].strip()
            usno_set = line[offset + 5 : offset + 9].strip()

            start_of_day = ephem.Date((year, month, day)) + 5 * ephem.hour

            o.date = start_of_day
            body.compute(o)

            if usno_rise:
                o.date = start_of_day + 1
                o.previous_rising(body)
                two_digit_compare('rise', usno_rise)

                o.date = start_of_day
                o.next_rising(body)
                two_digit_compare('rise', usno_rise)

            if usno_set:
                o.date = start_of_day + 1
                o.previous_setting(body)
                two_digit_compare('set', usno_set)

                o.date = start_of_day
                o.next_setting(body)
                two_digit_compare('set', usno_set)

# The actual function that drives the test.

class Mixin(object):
    def test_usno(self):

        content = open(self.path).read()
        g = globals()
        for obj in g.values():
            if (isinstance(obj, type) and issubclass(obj, Trial)
                and hasattr(obj, 'matches') and obj.matches(content)):
                trial_class = obj
                trial = trial_class()
                trial.path = self.path
                trial.run(content)
                return
        raise ValueError('Cannot find a test trial that recognizes %r'
                         % self.path)

#
# Auto-detect files
#

i = 1
for path in glob.glob('tests/usno/*.txt'):
    exec 'class T%d(unittest.TestCase, Mixin): path = %r' % (i, path)
    i += 1

if __name__ == '__main__':
    unittest.main()
