#!/usr/bin/env python2
'''
This script generates CSV compatible with https://www.glucosetracker.net/ app
from data stored on Abbott Optium Xido device.

You may consider it an example of glucolib.OptiumXido
'''

import glucolib
import sys

try:
    g = glucolib.OptiumXido()
    readings = g.fetchData()
    print '"Value","Category","Date","Time","Notes"'
    for type, value, date in readings:
        if type == 'G':
            print '"%d","","%s","%s",""' % (value, date.strftime('%m/%d/%Y'), date.strftime('%I:%M %p'))
            
except (glucolib.DeviceInvalid, glucolib.DeviceNotConnected), ex:
    print >>sys.stderr, "*** Make sure your device is connected properly and " \
        "not sleeping (you may want to replug the connector in such case)"
    if ex:
        print >>sys.stderr, "*** Captured exception:",ex
