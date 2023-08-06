'''Print yesterday's market clearing price/demand points and exit.'''

# Standard library imports
import sys
from StringIO import StringIO
import datetime
from pprint import pprint

# 3rd Party Libraries
from pyaeso import ets

def  main():
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(1)

    f = StringIO()
    ets.dump_pool_price(f, start_date, end_date)
    f.seek(0)
    #print f.getvalue()
    data = list(ets.parse_pool_price_file(f))
    f.close()

    pprint('''Yesterday's market clearing price/demand points.''')
    for d in data:
        # Time calculations are easier when done in UTC so that no timezone
        # conversions or daylist-savings time conversions need to be made.  For
        # this reason all times yielded by pyaeso are UTC.
        #
        # UTC times are converted to local times when they are displayed to the
        # user.
        print '{0} ${1} {2}MW'.format(d.t.astimezone(ets.ALBERTA_TZ), d.price, d.demand)

    return(0)


if __name__ == '__main__':
    sys.exit(main())
