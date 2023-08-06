'''Prints market participants in alphabetical order according to AESO ETS.'''

# Standard library imports
import sys
from StringIO import StringIO
import datetime
from pprint import pprint

# 3rd Party Libraries
from pyaeso import ets

def  main():
    f = ets.urlopen_asset_list()
    assets = list(ets.parse_asset_list_file(f))
    f.close()

    # Remove duplicates from list and sort
    participants = list(set([a.participant_name for a in assets]))
    participants.sort()

    print '''Market Participants in Alphabetical Order According to AESO ETS'''
    for p in participants:
        print repr(p)

    return(0)


if __name__ == '__main__':
    sys.exit(main())
