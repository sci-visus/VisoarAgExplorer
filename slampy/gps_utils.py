import pymap3d
import math
import numpy

# ////////////////////////////////////////////////////////////////////////
class GPSUtils:
	
	# gpsToLocalCartesian
	@staticmethod
	def gpsToLocalCartesian(lat,lon,lat0,lon0):
		ret=pymap3d.geodetic2enu(lat, lon, 0, lat0, lon0, 0)[0:2]
		return [it if isinstance(it, (int,float)) else it.item(0) for it in ret]
		
	#localCartesianToGps
	@staticmethod
	def localCartesianToGps(x,y,lat0,lon0):
		ret=pymap3d.enu2geodetic(x,y,0,lat0,lon0,0)[0:2]
		return [it if isinstance(it, (int,float)) else it.item(0) for it in ret]
		
	# from (lat,lon) to [0,1]
	@staticmethod
	def gpsToUnit(lat,lon):
		siny =  min(max(math.sin(lat* (math.pi / 180.0)), -.9999),.9999)
		ux = 0.5 + lon /360.0
		uy = 0.5 + 0.5 * math.log((1 + siny) / (1 - siny)) * -(0.5 / math.pi)
		ux,uy=ux,1.0-uy # scrgiorgio mirror Y
		return (ux,uy)

	# from [0,1] to lat,lon
	@staticmethod
	def unitToGPS(ux,uy):
		ux,uy=ux,1.0-uy # scrgiorgio mirror Y
		lat=(2.0 * math.atan(math.exp((uy - 0.5) / -(1.0 / (2.0 * math.pi)))) - math.pi / 2.0)/ (math.pi / 180.0)
		lon=(ux - 0.5) * 360.0
		return (lat,lon)
		
