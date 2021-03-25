import random
import urllib.request
import json

# TODO: remove this
# https://console.cloud.google.com/google/maps-apis/apis/maps-embed-backend.googleapis.com/credentials?folder=&organizationId=&project=visus-1536564808849&duration=PT1H
GoogleAPIKey="AIzaSyCdew7ZMCDW_1xoi69Xv_LsVC45aJd-8Ds"

# ////////////////////////////////////////////////////////////////////////////
# see https://github.com/vgm64/gmplot
class GoogleMaps:

	# constructor
	def __init__(self, level=16):
		self.min_lat,self.max_lat=None,None
		self.min_lon,self.max_lon=None,None
		self.content=[]
		self.content.append("""
			<html><head>
			<meta name="viewport" content="initial-scale=1.0, user-scalable=no" />
			<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>
			<title>Visus Slam </title>
			<script type="text/javascript" src='https://maps.googleapis.com/maps/api/js?libraries=visualization&key=%s'>
			</script>
			<script type="text/javascript">
			function initialize() {
				var map = new google.maps.Map(document.getElementById("map_canvas"), {zoom: %d,center: new google.maps.LatLng(TARGET_LAT, TARGET_LON) ,mapTypeId: google.maps.MapTypeId.SATELLITE});
			""" % (GoogleAPIKey, level))

	# addLatLon
	def addLatLon(self,lat,lon):
		self.min_lat=min([self.min_lat, lat]) if self.min_lat is not None else lat
		self.max_lat=max([self.max_lat, lat]) if self.max_lat is not None else lat
		self.min_lon=min([self.min_lon, lon]) if self.min_lon is not None else lon
		self.max_lon=max([self.max_lon, lon]) if self.max_lon is not None else lon

	# addMarker
	def addMarker(self,name, lat,lon, color="blue"):
		self.addLatLon(lat,lon)
		name=name.replace("\\","/")
		self.content.append("""
			new google.maps.Marker({title: '%s', icon: {url: 'http://maps.google.com/mapfiles/ms/icons/%s-dot.png'}, position: new google.maps.LatLng(%f, %f), map:map });
			""" % (name, color, lat, lon))



	# addPolyline
	def addPolyline(self,points,strokeColor="#FF0000", strokeOpacity="1.0", strokeWeight="2"):
		for lat,lon in points: 
			self.addLatLon(lat,lon)
		
		s_points=["{lat:%f, lng:%f}" % (lat,lon) for lat,lon in points]
		self.content.append("""
			var g_polyline=new google.maps.Polyline({path: [%s],geodesic: true,strokeColor: '%s',strokeOpacity: %s, strokeWeight: %s });
			g_polyline.setMap(map);
			""" % (",".join(s_points),strokeColor, strokeOpacity, strokeWeight))

	# generateHtml
	def generateHtml(self):
		self.content.append("""}
			</script>
			</head>
			<body style="margin:0px; padding:0px;" onload="initialize()">
			<div id="map_canvas" style="width: 100%; height: 100%;"></div>
			</body>
			</html>""")
		ret=" ".join(self.content)
		ret=ret.replace("TARGET_LAT",str((self.min_lat+self.max_lat)/2))
		ret=ret.replace("TARGET_LON",str((self.min_lon+self.max_lon)/2))
		return ret

# /////////////////////////////////////////////////////////////////////////////////////////////
# note: it costs 5$ for 1K request so keep it low)
def GoogleGetTerrainElevations(lats,lons,num_request=32):
	# google stop to answer if too many request
	url="https://maps.googleapis.com/maps/api/elevation/json?key=%s&locations=" % (GoogleAPIKey,)
	url+="|".join(["%f,%f" %(lats[I],lons[I]) for I in random.sample(range(len(lats)),min([num_request,len(lats)]))])
	print(url)
	content = urllib.request.urlopen(url).read()
	# print("Google url",url)
	# print("Google response: ",content)
	content=json.loads(content)
	ret=[result["elevation"] for result in content["results"]]
	print("result","\n",ret)
	return ret