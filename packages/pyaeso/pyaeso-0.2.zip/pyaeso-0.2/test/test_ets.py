import unittest
import os.path
from StringIO import StringIO
import datetime
import bz2

# 3rd Party Required Libraries
import pytz

# Custom Libraries
from pyaeso import ets


class TestDayBlockIt(unittest.TestCase):
    def test_iteration(self):
        start_date = datetime.date(1995, 1, 1)
        end_date = datetime.date(1995, 1, 10)

        it = ets.DayBlockIt(start_date, end_date, 10)
        self.assertEquals(it.next(), (start_date, end_date))
        self.assertRaises(StopIteration, it.next)

        it = ets.DayBlockIt(start_date, end_date, 5)
        self.assertEquals(it.next(), (datetime.date(1995, 1, 1), datetime.date(1995, 1, 5)))
        self.assertEquals(it.next(), (datetime.date(1995, 1, 6), datetime.date(1995, 1, 10)))
        self.assertRaises(StopIteration, it.next)


class TestPoolPrice(unittest.TestCase):
    def test_parse_pool_price_file(self):
        test_series_file = os.path.join(os.path.dirname(__file__), 'res', 'ets_testseries.csv.bz2')

        f = bz2.BZ2File(test_series_file)
        points = list(ets.parse_pool_price_file(f))
        self.assertEquals(len(points), 43057)
        f.close()

    def test_datetime_normalization(self):
        # Test DST handling
        lut = {
            # DST active
            "10/26/1996 00" : datetime.datetime(1996, 10, 26, 6),
            "10/26/1996 01" : datetime.datetime(1996, 10, 26, 7),
            "10/26/1996 02" : datetime.datetime(1996, 10, 26, 8),
            "10/26/1996 03" : datetime.datetime(1996, 10, 26, 9),

            # DST ends this day
            "10/27/1996 00" : datetime.datetime(1996, 10, 27, 6),
            "10/27/1996 01" : datetime.datetime(1996, 10, 27, 7),
            "10/27/1996 02" : datetime.datetime(1996, 10, 27, 8),
            "10/27/1996 02*" : datetime.datetime(1996, 10, 27, 9),
            "10/27/1996 03" : datetime.datetime(1996, 10, 27, 10),

            # DST inactive
            "10/28/1996 00" : datetime.datetime(1996, 10, 28, 7),
            "10/28/1996 01" : datetime.datetime(1996, 10, 28, 8),
            "10/28/1996 02" : datetime.datetime(1996, 10, 28, 9),
            "10/28/1996 03" : datetime.datetime(1996, 10, 28, 10),
        }
        for datetime_str, expected_utc_datetime in lut.items():
            self.assertEquals(ets._normalize_dtstr_to_utc(datetime_str), pytz.utc.localize(expected_utc_datetime))

        # Test handling of 24
        # '03/02/2005 24' -> 2009-03-03 0
        self.assertEquals(ets._normalize_dtstr_to_utc('03/02/2005 24'), ets.ALBERTA_TZ.localize(datetime.datetime(2005, 3, 3, 0)).astimezone(pytz.utc))


class TestAssetList(unittest.TestCase):
    def test_parse_asset_list_file(self):
        test_series_file = os.path.join(os.path.dirname(__file__), 'res', 'asset_list.csv.bz2')

        f = bz2.BZ2File(test_series_file)
        assets = list(ets.parse_asset_list_file(f))
        self.assertEquals(len(assets), 1862)
        for asset in assets:
            for char in '<>':
                # ETS embeds HTML anchors in the asset name.  Test to
                # make sure they have been properly stripped out.
                self.assertTrue(char not in asset.asset_name)
        f.close()



#~ class TestLiveEtsConnection(object):
class TestLiveEtsConnection(unittest.TestCase):
    def test_dump_asset_list(self):
        '''ETS-Coupled Test.'''
        f = StringIO()
        ets.dump_asset_list(f)
        assets = list(ets.parse_asset_list_file(f))
        f.close()

    def test_dump_pool_price_file(self):
        '''ETS-Coupled Test.'''
        f = StringIO()
        ets.dump_pool_price(f)
        f.seek(0)
        points = list(ets.parse_pool_price_file(f))
        f.close()


if __name__ == '__main__':
    unittest.main()
