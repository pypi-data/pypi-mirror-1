#~ pyaeso is a python package that makes access to the Alberta, Canada's
#~ Electric System Operator's (AESO) Energy Trading System (ETS) easier.

#~ Copyright (C) 2009 Keegan Callin

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

'''
'''

# Standard library imports
import urllib
import urllib2
import csv
import datetime
import time
import decimal
from decimal import Decimal
import shutil
import time
import sys
import re
from time import strptime
from time import mktime

# Other 3rd Party Libraries
import pytz

class DayBlockIt(object):
    '''Steps over blocks of days between two time periods.  Each call to
    next() will return a 2-tuple containing a start date and end date as
    far apart as is permitted by the /days/ parameter.

    Example
    >>> from pyaeso import ets
    >>> import datetime
    >>>
    >>> start_date = datetime.date(1995, 1, 1)
    >>> end_date = datetime.date(1995, 1, 10)
    >>>
    >>> it = ets.DayBlockIt(start_date, end_date, 4)
    >>> it.next()
    (datetime.date(1995, 1, 1), datetime.date(1995, 1, 4))
    >>> it.next()
    (datetime.date(1995, 1, 5), datetime.date(1995, 1, 8))
    >>> it.next()
    (datetime.date(1995, 1, 9), datetime.date(1995, 1, 10))
    >>> it.next()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "pyaeso/ets.py", line 65, in next
        raise StopIteration()
    StopIteration
    '''

    def __init__(self, start_date, end_date, days):
        '''Create an object that iterates blocks of start/end dates of length
        /days/.

        start_date - (datetime.date)
        end_date - (datetime.date)
        days - (int) maximum number of days in each steps.
        '''
        self._start_date = start_date
        self._end_date = end_date
        self._days = days

        self._now = self._start_date


    def __iter__(self):
        return self


    def next(self):
        if self._now:
            start_date = self._now
            end_date = self._now + datetime.timedelta(self._days - 1)

            if end_date >= self._end_date:
                end_date = self._end_date
                self._now = None
            else:
                self._now = self._now + datetime.timedelta(self._days)

            return (start_date, end_date)
        else:
            raise StopIteration()


def urlopen_pool_price(start_date, end_date):
    '''Returns a file-like object containing data returned by the ETS
    pool price webservice.

    Note that the webservice limits the number of days that can be queried
    to 721 days (as of 2009-11-12).

    @type  start_date: datetime.date
    @type  end_date: datetime.date
    @return: file-like object as returned by urlopen.
    '''
    DATE_FORMAT = '%m%d%Y'

    url = 'http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalPoolPriceReportServlet'
    parameters = {
        'contentType' : 'csv',
        'beginDate' : start_date.strftime(DATE_FORMAT),
        'endDate' : end_date.strftime(DATE_FORMAT),
    }

    encoded_params = urllib.urlencode(parameters)
    #http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalPoolPriceReportServlet?contentType=html&beginDate=08012009&endDate=08112009
    f = urllib2.urlopen(url, encoded_params)

    return f


def urlopen_asset_list():
    '''Returns a file-like object containing data returned by the ETS
    asset list webservice.

    @return: file-like object as returned by urlopen.
    '''
    url = 'http://ets.aeso.ca/ets_web/ip/Market/Reports/AssetListReportServlet'
    parameters = {
        'contentType' : 'csv',
    }

    encoded_params = urllib.urlencode(parameters)
    #http://ets.aeso.ca/ets_web/ip/Market/Reports/AssetListReportServlet?contentType=html
    f = urllib2.urlopen(url, encoded_params)

    return f


def dump_pool_price(f_out, start_date = datetime.date(1995, 1, 1), end_date = datetime.date.today() + datetime.timedelta(1)):
    '''Downloads data from ETS.'''

    for (start, end) in DayBlockIt(start_date, end_date, 721):
        # print 'From', start, 'to', end
        f_in = urlopen_pool_price(start, end)
        shutil.copyfileobj(f_in, f_out)

        if end < end_date:
            time.sleep(10)


def dump_asset_list(f_out):
    f_in = urlopen_asset_list()
    shutil.copyfileobj(f_in, f_out)


_RE_DATEHOUR = re.compile('(\d+)/(\d+)/(\d+) (\d+)$')
ALBERTA_TZ = pytz.timezone('America/Edmonton')

def _normalize_dtstr_to_utc(datetime_str):
    # Sample line:
    # ['Date (HE)', 'Price ($)', '30Ravg ($)', 'System Demand (MW)']
    # ['08/10/2009 15', '67.36', '39.67', '8623.0']
    datetime_str = datetime_str.strip()
    starred = False

    # Construct a naive datetime object
    try:
        if datetime_str.endswith('*'):
            starred = True
            datetime_str = datetime_str[0:-1]

        # This series is to support Python < 2.5
        struct_time = strptime(datetime_str, "%m/%d/%Y %H")
        timestamp = mktime(struct_time)
        t = datetime.datetime.fromtimestamp(timestamp)

        # Python >= 2.5
        # t = datetime.datetime.strptime(datetime_str, "%m/%d/%Y %H")

        # This code segment verifies that the Python 2.4 code section
        # above is equivalent to the Python >= 2.5 version.
        #~ if datetime.datetime.strptime(datetime_str, "%m/%d/%Y %H") != t:
            #~ raise ValueError('Problem!')

    except ValueError:
        # Often receive a line like this.
        # ['07/31/2009 24', '36.78', '41.83', '7556.0']
        #
        # AESO clock goes from 1-24 hours instead of expected
        # range of 0-23.
        #
        # Compensating for this strangeness
        miscreant_str = datetime_str
        match = _RE_DATEHOUR.match(miscreant_str)
        if match:
            year = int(match.group(3))
            month = int(match.group(1))
            day = int(match.group(2))
            hour = int(match.group(4))

            if hour == 24:
                t = datetime.datetime(year, month, day, 0) + datetime.timedelta(1)
            else:
                raise
        else:
            raise

    # Localize naive datetime objects.
    #
    # On a Daylight-Savings-Time (DST) switch, AESO hours are counted:
    # 1, 2, 2*
    #
    # Need to translate this to:
    # 1 (with is_dst option set to True), 1 (with is_dst option set to False), 2
    #
    if t.hour == 2 and not starred:
        # Testing to see if this second-hour of the day occurs
        # after a DST transition
        dst_test_time = datetime.datetime(t.year, t.month, t.day, t.hour - 1)
        try:
            ALBERTA_TZ.localize(dst_test_time, is_dst = None)
        except pytz.AmbiguousTimeError:
            # This "2" occurs after a DST transition
            ab_dt = ALBERTA_TZ.localize(dst_test_time, is_dst = False)
        else:
            # This "2" does not occur after a DST transition; no is_dst necessary
            ab_dt = ALBERTA_TZ.localize(t, is_dst = None)
    else:
        try:
            ab_dt = ALBERTA_TZ.localize(t, is_dst = None)
        except pytz.AmbiguousTimeError:
            if t.hour == 1 and not starred:
                # First hour occurring before a DST jump.
                ab_dt = ALBERTA_TZ.localize(t, is_dst = True)
            else:
                raise

    # convert from Alberta time to UTC time
    return pytz.utc.normalize(ab_dt.astimezone(pytz.utc))


class EtsPoint(object):
    def __init__(self, t, price, demand):
        self._t = t
        self._price = price
        self._demand = demand

    @property
    def t(self):
        return self._t

    @property
    def price(self):
        return self._price

    @property
    def demand(self):
        return self._demand

    @classmethod
    def from_csvline(cls, line):
        # Sample line:
        # ['Date (HE)', 'Price ($)', '30Ravg ($)', 'System Demand (MW)']
        # ['08/10/2009 15', '67.36', '39.67', '8623.0']

        # Normalize time string to UTC time.
        t = _normalize_dtstr_to_utc(line[0])
        price = Decimal(line[1])
        demand = Decimal(line[3])

        point = EtsPoint(t, price, demand)

        return point


def parse_pool_price_file(f):
    '''Yields EtsPoint tuples as extracted from the open CSV file f.'''
    reader = csv.reader(f)
    for idx, line in enumerate(reader):
        # ['Date (HE)', 'Price ($)', '30Ravg ($)', 'System Demand (MW)']
        # ['08/10/2009 15', '67.36', '39.67', '8623.0']
        try:
            try:
                yield EtsPoint.from_csvline(line)
            except ValueError, e:
                #~ if line[0].strip().endswith('*'):
                    #~ # Star exists in output (meaning is unknown)
                    #~ # ignore this point.
                    #~ pass
                if line[0].strip() == '' or \
                    line[0].strip() == 'Pool Price' or \
                    line[0].strip() == 'Date (HE)':
                    # Date string is empty.  This is a header line or
                    # blank line.
                    pass
                else:
                    raise
            except IndexError, e:
                # Ignore the line; it does not have the right number of cells.
                # It may, for example, be blank.
                pass
            except decimal.InvalidOperation, e:
                if line[1].strip() == '-':
                    # No price data available. Ignore point.
                    pass
                else:
                    raise
        except (ValueError, IndexError, decimal.InvalidOperation), e:
            raise ValueError('Unable to parse line {0}: {1}'.format(idx, repr(line)))


class AssetType(object):
    SOURCE = 'source'
    SINK = 'sink'

    _lut = {
        SOURCE : 'source',
        SINK : 'sink',
    }

    @classmethod
    def from_str(klass, string):
        normalized = string.strip().lower()

        try:
            return klass._lut[normalized]
        except KeyError:
            raise ValueError('Unknown asset type {0}.'.format(repr(string)))


class AssetStatus(object):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    RETIRED = 'retired'
    SUSPENDED = 'suspended'

    _lut = {
        ACTIVE : 'active',
        INACTIVE : 'inactive',
        RETIRED : 'retired',
        SUSPENDED : 'suspended',
    }

    @classmethod
    def from_str(klass, string):
        normalized = string.strip().lower()

        try:
            return klass._lut[normalized]
        except KeyError:
            raise ValueError('Unknown asset status {0}.'.format(repr(string)))


_RE_ASSETNAME = re.compile('<[^>]*>\s*<[^>]*>(.*)')
def _normalize_asset_name(string):
    #'<A NAME=3Anchor"></A>301A 3070 Ret #1'
    match = _RE_ASSETNAME.match(string)
    if match:
        return match.group(1)
    else:
        return string


class Asset(object):
    def __init__(self, asset_name, asset_id, asset_type, status, participant_name, participant_id):
        self._asset_name = asset_name
        self._asset_id = asset_name
        self._asset_type = asset_type
        self._status = status
        self._participant_name = participant_name
        self._participant_id = participant_id

    @property
    def asset_name(self):
        return self._asset_name

    @property
    def asset_id(self):
        return self._asset_id

    @property
    def asset_type(self):
        return self._asset_type

    @property
    def status(self):
        return self._status

    @property
    def participant_name(self):
        return self._participant_name

    @property
    def participant_id(self):
        return self._participant_id


def parse_asset_list_file(f):
    '''Yields tuples as extracted from the open CSV file f.'''
    reader = csv.reader(f)
    for idx, line in enumerate(reader):
        # ["Williams Lk Gen St - BCH","IPI1","Source","Retired","Inland Pacific Energy Services","IPES"]
        try:
            if idx > 2 and len(line) > 0:
                yield Asset(_normalize_asset_name(line[0]), line[1], AssetType.from_str(line[2]), AssetStatus.from_str(line[3]), line[4], line[5])
        except IndexError:
            # raised when number of cells in row is incorrect.
            raise ValueError('Unable to parse line {0}: {1}'.format(idx, repr(line)))

