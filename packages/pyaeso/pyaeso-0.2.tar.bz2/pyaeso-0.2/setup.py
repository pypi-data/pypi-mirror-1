from distutils.core import setup

NAME = 'pyaeso'
VERSION = '0.2'
DOWNLOAD_URL = 'http://pypi.python.org/pypi/pyaeso'

def long_description():
    f = open('README.txt')
    text = f.read()
    f.close()
    return text


DESCRIPTION = "Pythonic access to the Alberta (Canada) Electric System Operator (AESO) Energy Trading System (ETS)."
LONG_DESCRIPTION = long_description()
CLASSIFIERS = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.4",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Libraries :: Python Modules",
]


setup(
    name = NAME,
    packages = ["pyaeso"],
    version = VERSION,
    description = DESCRIPTION,
    author = "Keegan Callin",
    author_email = "kc@kcallin.net",
    url = "http://bitbucket.org/kc/pyaeso/wiki/Home",
    download_url = DOWNLOAD_URL,
    keywords = [],
    license = 'GNU General Public License Version 3 (GPLv3)',
    requires=['pytz'],
    classifiers = CLASSIFIERS,
    long_description = LONG_DESCRIPTION
)
