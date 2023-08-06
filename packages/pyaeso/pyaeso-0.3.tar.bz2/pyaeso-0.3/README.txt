======
pyaeso
======

pyaeso  is a python package that makes access to the Alberta Electric
System Operator's (AESO) Energy Trading System (ETS) easier.

The Alberta Electric Systems Operator (AESO) <http://www.aeso.ca>
operates the Canadian province of Alberta's deregulated electricity
market.  AESO provides price, demand, and other valuable information
through the publically accessible Energy Trading System (ETS) website
<http://ets.aeso.ca>.  This information is useful for economic
analysis, power trading, electric system study, and electric system
forecasting.  The first step in using such information is to download
it and parse it into useful data structures - a task performed by this
library.  Typically the data will feed statistical methods, heuristics,
and system models to provide useful analysis of the Alberta electric
system.

The pyaeso project is hosted at <http://bitbucket.org/kc/pyaeso> and
releases are made via the Python Package Index at
<http://pypi.python.org/pypi/pyaeso>.  Online documentation is available
at <http://packages.python.org/pyaeso>.


Requirements
============
* *Python 2.4 or better* - Available at <http://python.org/download>
  (2009-11-25).

* *pytz* - "World timezone definitions, modern and historical".
  Available at <http://pypi.python.org/pypi/pytz> (2009-11-14).


Installation
============

Extract the archive, enter the recovered directory and type:

``python setup.py install``


Usage
=====

Some code samples that use pyaeso are availble in the ``examples``
directory.  One sample is listed here::

    >>> ''Print yesterday's market clearing price/demand points and exit.'''
    >>>
    >>> # Standard library imports
    >>> import sys
    >>> from StringIO import StringIO
    >>> import datetime
    >>>
    >>> # 3rd Party Libraries
    >>> from pyaeso import ets
    >>>
    >>> end_date = datetime.date.today()
    >>> tart_date = end_date - datetime.timedelta(1)
    >>>
    >>> f = StringIO()
    >>> ets.dump_pool_price(f, start_date, end_date)
    >>> f.seek(0)
    >>> #print f.getvalue()
    >>> data = list(ets.parse_pool_price_file(f))
    >>> f.close()
    >>>
    >>> print '''Yesterday's market clearing price/demand points.'''
    >>> for d in data:
    >>>     print d.t.astimezone(ets.ALBERTA_TZ), '$' + str(d.price), str(d.demand) + 'MW'


Known Incompatibilities
=======================

* *Python <= 2.3* - Fails because pyaeso uses several standard library
  modules that were introduced in Python 2.4.

* *Python 3* - pyaeso uses the pytz package which has no Python 3
  version (2009-11-14).  The pyaeso library should be quickly available
  for Python 3 once pytz is updated.


Bugs and Enhancements
=====================

If you would like to file a bug report or feature request then you can
do so at <http://bitbucket.org/kc/pyaeso/issues>.


Contact
=======

As the maintainer of this library I, Keegan Callin, would welcome your
polite, constructive comments and criticisms of this library.  I can
be reached by email using the address kc (at) kcallin.net.  If you need
to talk to me on the telephone or send me something by snail mail, send
me an email and I'll gladly mail you instructions on how to reach me.
