#!/usr/bin/env python2
'''
This script generates CSV compatible with https://www.glucosetracker.net/ app
from data stored on Abbott Optium Xido or Diagnosis Diagnostic Gold device.

You may consider it an example of glucolib.
'''

import glucolib
import sys

devices = glucolib.list_devices()
if not devices:
    print >>sys.stderr, "*** No supported devices found"
    exit(1)

try:
    g = devices[0][1](devices[0][0])
    readings = g.fetch_data()
    print '"Value","Category","Date","Time","Notes"'
    for type, value, date in readings:
        if type == 'G':
            print '"%d","","%s","%s",""' % (value, date.strftime('%m/%d/%Y'),
                                            date.strftime('%I:%M %p'))

except (glucolib.DeviceInvalid, glucolib.DeviceNotConnected), ex:
    print >>sys.stderr, "*** Make sure your device is connected properly and "\
        "not sleeping (you may want to replug the connector in some cases)"
    print >>sys.stderr, "*** Captured exception:", ex
    exit(1)
