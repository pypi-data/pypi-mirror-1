#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Copyright (C) 2009 Daniel Fett
#     This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Author: Daniel Fett advancedcaching@fragcom.de
#

import geo
import urllib
import json

class Geonames():
    URL = 'http://ws.geonames.org/searchJSON?formatted=true&q=%s&maxRows=1&lang=es&style=short'
    def __init__(self, downloader):
        self.downloader = downloader

    def search(self, string):
        print "* Trying to search geonames for %s" % string
        page = self.downloader.get_reader(url = self.URL % urllib.quote(string)).read()
        values = json.loads(page)
        if int(values['totalResultsCount']) == 0:
            raise Exception('No Record found for query "%s"' % string)
        res = values['geonames'][0]
        c = geo.Coordinate(float(res['lat']), float(res['lng']), string)
        print "* Using %s for query '%s'" % (c, string)
        return c