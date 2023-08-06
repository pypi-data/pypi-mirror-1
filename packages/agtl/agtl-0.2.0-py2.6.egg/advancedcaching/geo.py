#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

import re

class Coordinate():
    SQLROW = {'lat': 'REAL', 'lon': 'REAL', 'name': 'TEXT'}
	
    FORMAT_D = 0
    FORMAT_DM = 1
    re_to_dm_array = re.compile('^(\d?)(\d)(\d) (\d)(\d)\.(\d)(\d)(\d)$')
    re_to_d_array = re.compile('^(\d?)(\d)(\d).(\d)(\d)(\d)(\d)(\d)$')
	
    def __init__(self, lat, lon, name="No Name"):
	self.lat = lat
	self.lon = lon
	self.name = name
		
    def from_d(self, lat, lon):
	self.lat = lat
	self.lon = lon
		
    def __from_dm(self, latdd, latmm, londd, lonmm):
	self.lat = latdd + (latmm / 60)
	self.lon = londd + (lonmm / 60)
		
    def from_dm_array(self, sign_lat, lat, sign_lon, lon):
	self.__from_dm(sign_lat * (lat[0] * 10 + lat[1]),
		       float(str(lat[2]) + str(lat[3]) + "." + str(lat[4]) + str(lat[5]) + str(lat[6])),
		       sign_lon * (lon[0] * 100 + lon[1] * 10 + lon[2]),
		       float(str(lon[3]) + str(lon[4]) + "." + str(lon[5]) + str(lon[6]) + str(lon[7])))

    def from_d_array(self, sign_lat, lat, sign_lon, lon):
	self.lat = int(sign_lat) * float("%d%d.%d%d%d%d%d" % tuple(lat))
	self.lon = int(sign_lon) * float("%d%d%d.%d%d%d%d%d" % tuple(lon))
			
    def to_dm_array(self):
	[[lat_d, lat_m], [lon_d, lon_m]] = self.to_dm()
		
	d_lat = self.re_to_dm_array.search("%02d %06.3f" % (abs(lat_d), abs(lat_m)))
	d_lon = self.re_to_dm_array.search("%03d %06.3f" % (abs(lon_d), abs(lon_m)))
	return [
	    [d_lat.group(i) for i in xrange (2, 9)],
	    [d_lon.group(i) for i in xrange (1, 9)]
	    ]

    def to_d_array(self):

	d_lat = self.re_to_d_array.search("%08.5f" % abs(self.lat))
	d_lon = self.re_to_d_array.search("%09.5f" % abs(self.lon))
	return [
	    [d_lat.group(i) for i in xrange (2, 7)],
	    [d_lon.group(i) for i in xrange (1, 7)]
	    ]
		
    def to_dm(self):
	return [[int(math.floor(self.lat)), (self.lat - math.floor(self.lat)) * 60],
	    [int(math.floor(self.lon)), (self.lon - math.floor(self.lon)) * 60]]
	
    def bearing_to(self, target):
	lat1 = math.radians(self.lat)
	lat2 = math.radians(target.lat)
	#lon1 = math.radians(self.lon)
	#lon2 = math.radians(target.lon)
		
	dlon = math.radians(target.lon - self.lon);
	y = math.sin(dlon) * math.cos(lat2)
	x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
	bearing = math.degrees(math.atan2(y, x))
	return (360 + bearing) % 360

    def get_lat(self, format):
	l = abs(self.lat)
	if self.lat > 0:
	    c = 'N'
	else:
	    c = 'S'
	if format == self.FORMAT_D:
	    return "%s%8.5f°" % (c, l)
	elif format == self.FORMAT_DM:
	    return "%s%2d° %06.3f'" % (c, math.floor(l), (l - math.floor(l)) * 60)

    def get_lon(self, format):
	l = abs(self.lon)
	if self.lon > 0:
	    c = 'E'
	else:
	    c = 'W'
	if format == self.FORMAT_D:
	    return "%s%9.5f°" % (c, l)
	elif format == self.FORMAT_DM:
	    return "%s%3d° %06.3f'" % (c, math.floor(l), (l - math.floor(l)) * 60)

    def distance_to (self, target):
	R = 6371000;
	dlat = math.pow(math.sin(math.radians(target.lat-self.lat) / 2), 2)
	dlon = math.pow(math.sin(math.radians(target.lon-self.lon) / 2), 2)
	a = dlat + math.cos(math.radians(self.lat)) * math.cos(math.radians(target.lat)) * dlon;
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a));
	return R * c;

    def __str__(self):
	return "%s %s" % (self.get_lat(Coordinate.FORMAT_DM), self.get_lon(Coordinate.FORMAT_DM))
		
    def serialize(self):

	return {'lat': self.lat, 'lon': self.lon, 'name': self.name}
		
    def unserialize(self, data):
	self.lat = data['lat']
	self.lon = data['lon']
	self.name = data['name']
	
