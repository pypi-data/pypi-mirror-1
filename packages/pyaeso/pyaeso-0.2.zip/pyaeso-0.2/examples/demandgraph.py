# Standard library imports
import datetime
import time
import decimal
from decimal import Decimal
import collections
import time
import sys
import re
import stat
import os
import os.path
import math

# Plotting libraries
NUMPY = 'numpy'
MATPLOTLIB = 'matplotlib'
PYAESO = 'pyaeso'
package_urls = {
    NUMPY : 'http://numpy.scipy.org',
    MATPLOTLIB : 'http://matplotlib.sourceforge.net',
    PYAESO : 'http://bitbucket.org/kc/pyaeso/wiki/Home',
}

missing_packages = []
try:
    import numpy
except ImportError:
    missing_packages.append(NUMPY)

try:
    import matplotlib.pyplot as plt
    import matplotlib.mlab as mlab
    import matplotlib.ticker as ticker
    import pylab
except ImportError:
    missing_packages.append(MATPLOTLIB)

# Other 3rd Party Libraries
try:
    from pyaeso import ets
except ImportError:
    missing_packages.append(PYAESO)

if missing_packages:
    if len(missing_packages) == 1:
        print 'A required package is missing.  Please install it before proceeding.'
    else:
        print 'Please install the following missing packages before proceeding.'

    for m in missing_packages:
        print '* {} from ({})'.format(m, package_urls[m])

DATAFILE = '/tmp/ets-data.dat'
CACHEFILE = '/tmp/data-cache.npy'

class EtsPointSeries(object):
    def __init__(self, t, price, demand):
        self.t = numpy.array(t)
        self.price = numpy.array(price)
        self.demand = numpy.array(demand)

        if len(self.t)  != len(self.price) or len(self.t) != len(self.demand):
            raise IndexError('Lists t, price, and demand must all have the same length')


    @classmethod
    def from_pointlist(klass, pointlist):
        t = [p.t for p in pointlist]
        price = [float(p.price) for p in pointlist]
        demand = [float(p.demand) for p in pointlist]

        return EtsPointSeries(t, price, demand)


    def __len__(self):
        return len(self.t)


class FigureData(object):
    def __init__(self,
            t,
            demand_series,
            price_series,
            range_t,
            demand_min_series,
            demand_max_series,
            price_min_series,
            price_max_series):
        self.t = t
        self.demand_series = demand_series
        self.price_series = price_series

        self.range_t = range_t
        self.demand_min_series = demand_min_series
        self.demand_max_series = demand_max_series
        self.price_min_series = price_min_series
        self.price_max_series = price_max_series


        if len(self.t) != len(self.demand_series):
            raise IndexError('Array t must have the same length as demand_series.')
        elif len(self.range_t) != len(self.demand_min_series) or \
                len(self.range_t) != len(self.demand_max_series):
            raise IndexError('Array range_t must have the same length as demand_min_series and demand_max_series.')
        elif len(self.t) != len(self.price_series):
            raise IndexError('Array t must have the same length as price_series.')
        elif len(self.range_t) != len(self.price_min_series) or \
                len(self.range_t) != len(self.price_max_series):
            raise IndexError('Array range_t must have the same length as price_min_series and price_max_series.')
        self._create_model()


    def _create_model(self):
        # Graph different models
        # evaluate at points indicated by model_times
        SECONDS_IN_YEAR = 365*24*60*60

        #model_times = list(times)
        #X_MAX = time.mktime(datetime.datetime(2030, 1, 1).timetuple())
        #X_MIN = times[0]
        #while True:
            #next_time = time.mktime((datetime.datetime.fromtimestamp(model_times[-1]) + datetime.timedelta(7*8)).timetuple())
            #if next_time < X_MAX:
                #model_times.append(next_time)
            #else:
                #break

        #~ linear_model_p = numpy.polyfit(times, demand_mw, 1)
        #~ linear_model_demand_f = numpy.poly1d(linear_model_p)
        #~ linear_model_demand_mw = [linear_model_demand_f(t) for t in model_times]

        #~ def log_model_demand_f(t):
            #~ log_model_growth = 0.034
            #~ return linear_model_demand_f(times[0])*math.e**(log_model_growth*((t - times[0])/SECONDS_IN_YEAR))
        #~ log_model_demand_mw = [log_model_demand_f(t) for t in model_times]

        #~ print 'Polynomial coefficients:', linear_model_p
        #~ print 'Annualized growth:', str(linear_model_p[0]*SECONDS_IN_YEAR) + 'MW'


    def save(self, f):
        numpy.save(f, self.t)
        numpy.save(f, self.demand_series)
        numpy.save(f, self.price_series)
        numpy.save(f, self.range_t)
        numpy.save(f, self.demand_min_series)
        numpy.save(f, self.demand_max_series)
        numpy.save(f, self.price_min_series)
        numpy.save(f, self.price_max_series)


    @classmethod
    def load(klass, f):
        t = numpy.load(f)
        demand_series = numpy.load(f)
        price_series = numpy.load(f)
        range_t = numpy.load(f)
        demand_min_series = numpy.load(f)
        demand_max_series = numpy.load(f)
        price_min_series = numpy.load(f)
        price_max_series = numpy.load(f)

        return klass(t, demand_series, price_series, range_t, demand_min_series, demand_max_series, price_min_series, price_max_series)







class BlockIt(object):
    def __init__(self, list, size, mode = 'full'):
        self._list = list
        self._size = size
        self._idx = 0
        self._mode = mode

    def __iter__(self):
        return self

    def next(self):
        if self._idx >= len(self._list):
            raise StopIteration()
        else:
            next_block = self._list[self._idx : self._idx + self._size]
            self._idx = self._idx + self._size

            if self._mode == 'valid' and len(next_block) != self._size:
                raise StopIteration()

            return next_block


class WindowIt(object):
    def __init__(self, list, size):
        self._list = list
        self._size = size
        self._idx = 0

    def __iter__(self):
        return self

    def next(self):
        if self._idx >= len(self._list):
            raise StopIteration()
        else:
            next_window = self._list[self._idx : self._idx + self._size]
            self._idx = self._idx + 1

            return next_window


def sliding_avg_filter(array, size = 30):
    return numpy.convolve(array, 1./size * numpy.ones(size), mode = 'valid')


def sliding_max_filter(array, size = 30):
    sliding_max = []

    for window in WindowIt(array, size):
        if len(window) == size:
            sliding_max.append(max(window))

    return numpy.array(sliding_max)


def sliding_min_filter(array, size = 30):
    sliding_min = []

    for window in WindowIt(array, size):
        if len(window) == size:
            sliding_min.append(min(window))

    return numpy.array(sliding_min)


def block_avg_filter(array, size = 30):
    sliding_avg = sliding_avg_filter(array, size)

    block_avg = numpy.empty(len(array)/size)

    for i in xrange(len(block_avg)):
        block_avg[i] = sliding_avg[i*size]

    return numpy.array(block_avg)


def block_max_filter(array, size = 30):
    block_max = []

    for block in BlockIt(array, size, mode = 'valid'):
        block_max.append(max(block))

    return numpy.array(block_max)


def block_min_filter(array, size = 30):
    block_min = []

    for block in BlockIt(array, size, mode = 'valid'):
        block_min.append(min(block))

    return numpy.array(block_min)


def ademand_figure(data):
    '''Plots market clearing volume using actual volume, maximum volume, and
    minimum volume information.  Plot a best-fit line using linear regression
    and using AESO's demand estimate.'''

    t = data.t
    demand_series = data.demand_series
    range_t = data.range_t
    demand_min_series = data.demand_min_series
    demand_max_series = data.demand_max_series

    # Date formatter
    def format_date(x, pos=None):
        text = datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d')
        return text

    # Create figure and setup graph
    fig = plt.figure()
    graph = fig.add_subplot(1, 1, 1)
    graph.set_title('Power Demand (MW) vs. Date')
    graph.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    graph.set_xlabel('Date')
    graph.set_ylabel('Power Demand (MW)')
    graph.grid(True)
    fig.autofmt_xdate()

    # Plot
    graph.fill_between(range_t, demand_min_series, demand_max_series, color='#e0e0ff')

    graph.plot(t, demand_series, '-')
    #~ graph.plot(model_times, linear_model_demand_mw, '-', color = 'red')
    #~ graph.plot(model_times, log_model_demand_mw, '-', color = 'grey')

    ymin, ymax = graph.get_ylim()
    if ymin > 0.:
        ymin = 0.
    graph.set_ylim(ymin, ymax)

    # Write graph to output
    return fig


def aprice_figure(data):
    '''Plots market clearing volume using actual volume, maximum volume, and
    minimum volume information.  Plot a best-fit line using linear regression
    and using AESO's demand estimate.'''

    t = data.t
    price_series = data.price_series
    range_t = data.range_t
    price_min_series = data.price_min_series
    price_max_series = data.price_max_series

    # Date formatter
    def format_date(x, pos=None):
        text = datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d')
        return text

    # Create figure and setup graph
    fig = plt.figure()
    graph = fig.add_subplot(1, 1, 1)
    graph.set_title('Power Price($/MW) vs. Date')
    graph.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    graph.set_xlabel('Date')
    graph.set_ylabel('Power Price ($/MW)')
    graph.grid(True)
    fig.autofmt_xdate()

    # Plot
    #graph.fill_between(range_t, price_min_series, price_max_series, color='#e0e0ff')

    graph.plot(t, price_series, '-')

    ymin, ymax = graph.get_ylim()
    if ymin > 0.:
        ymin = 0.
    graph.set_ylim(ymin, ymax)

    # Write graph to output
    return fig


def create_figure_data(f, dump_timing = False):
    # Load data file
    data = [d for d in ets.parse_pool_price_file(f) if d.demand is not None]

    # Convert list to numpy arrays
    series = EtsPointSeries.from_pointlist(data)

    # Calculate some point averages.
    size = 7*24
    avg_t = numpy.array([time.mktime(series.t[i].timetuple()) for i in xrange(size - 1, len(series.t), size)])
    demand_avg_series = block_avg_filter(series.demand, size = size)
    price_avg_series = block_avg_filter(series.price, size = size)

    ###################
    ## Calculate Max/min

    # Calculate min series
    size = 365*24
    range_t = numpy.array([time.mktime(series.t[i].timetuple()) for i in xrange(size - 1, len(series.t), size)])
    demand_min_series = block_min_filter(series.demand, size = size)
    price_min_series = block_min_filter(series.price, size = size)

    # Calculate max series
    demand_max_series = block_max_filter(series.demand, size = size)
    price_max_series = block_max_filter(series.price, size = size)

    return FigureData(avg_t, demand_avg_series, price_avg_series, range_t, demand_min_series, demand_max_series, price_min_series, price_max_series)


def  main():
    if not os.path.isfile(DATAFILE):
        with open(DATAFILE, 'a') as f:
            start_date = datetime.date(1995, 1, 1)
            end_date = datetime.date.today()

            ets.dump_pool_price(f, start_date, end_date)

    with open(DATAFILE) as f:
        data = create_figure_data(f, dump_timing = True)

    with open(CACHEFILE, 'wb') as f:
        data.save(f)

    with open(CACHEFILE, 'rb') as f:
        data = FigureData.load(f)

    fig = ademand_figure(data)
    print 'Generating demand-current.pdf'
    with open('demand-current.pdf', 'wb') as f:
        #pylab.savefig(f, format='png', dpi=150, transparent=False, bbox_inches="tight", pad_inches=0.1)
        #pylab.savefig(f, format='pdf', transparent=False, bbox_inches="tight", pad_inches=0.1, orientation = 'landscape', papertype = 'letter')
        fig.savefig(f, format='pdf', transparent=False, bbox_inches="tight", pad_inches=0.1, orientation = 'landscape', papertype = 'letter')

    print 'Generating price-current.pdf'
    fig = aprice_figure(data)
    with open('price-current.pdf', 'wb') as f:
        fig.savefig(f, format='pdf', transparent=False, bbox_inches="tight", pad_inches=0.1, orientation = 'landscape', papertype = 'letter')

    return 0


if __name__ == '__main__':
    sys.exit(main())