from geopy.geocoders import GoogleV3
geolocator = GoogleV3()
location = geolocator.reverse("52.509669, 13.376294")
print(location.address)