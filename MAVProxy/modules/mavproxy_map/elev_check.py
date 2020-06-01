#!/usr/bin/python
'''
Wrapper for the SRTM module (srtm.py)
It will grab the altitude of a long,lat pair from the SRTM database
Created by Stephen Dade (stephen_dade@hotmail.com)
'''

import os
import sys
import time

import numpy

from MAVProxy.modules.mavproxy_map import mp_elevation
import matplotlib.pyplot as plt

if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser("mp_elevation.py [options]")
    parser.add_option("--lat", type='float', default=-35.052544, help="start latitude")
    parser.add_option("--lon", type='float', default=149.509165, help="start longitude")
    parser.add_option("--database", type='string', default='srtm', help="elevation database")
    parser.add_option("--debug", action='store_true', help="enabled debugging")
    parser.add_option("--step", type='float', default=0.001)
    parser.add_option("--numsteps", type='int', default=1000)

    (opts, args) = parser.parse_args()

    EleModel = mp_elevation.ElevationModel(opts.database, debug=opts.debug)

    lat = opts.lat
    lon = opts.lon

    xdata = []
    ydata = []

    for x in range(opts.numsteps):
        xdata.append(lon)
        alt = EleModel.GetElevation(lat, lon, timeout=10)
        ydata.append(alt)
        if alt is None:
            print("Tile not available")
            sys.exit(1)
        lon += opts.step

    plt.plot(xdata, ydata, marker='+')
    plt.xlabel('Longitude(deg)')
    plt.ylabel('Altitude(m)')
    plt.show()
