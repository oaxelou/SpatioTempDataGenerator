# Axelou Olympia, December 2020
# Greece, University of Thessaly, dpt. Electrical & Computer Engineering
#
# Project: Spatio-temporal and spatio-textual data generator
# Supervisor: Vassilakopoulos Michail
#
# This file consists of auxiliary functions that aid in the 
# connection between the main code and the Google Maps API. In particular,
# Google Directions API and Google Static Map API.

import requests
import json
import string 

alphabet = dict(zip(range(0,26), string.ascii_uppercase))

apiKey = "&key=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
allow_api_calls = True
debug=False

# This function gets as input the coordinates of two POIs, performs
# a call to the Google Directions API in order to receive & return the duration 
# & the distance of the transportation from the origin POI to the destination.
def google_directions_api(coordinates_origin, coordinates_destination):
	url = 'https://maps.googleapis.com/maps/api/directions/json?'
	url += 'origin=' + coordinates_origin
	url += '&destination=' + coordinates_destination
	#url += '&mode=walking' # defaults to driving
	url += apiKey
	# print(url)
	if allow_api_calls:
		response = requests.get(url)
		json_data = json.loads(response.text)

		distance = -1
		duration = -1
		# print(json_data['status'])
		if json_data['status'] == 'OK':
			distance = json_data['routes'][0]['legs'][0]['distance']['value']
			duration = json_data['routes'][0]['legs'][0]['duration']['value']
	else:
		distance = 0
		duration = 300
	# print(distance, duration)
	return (distance, duration)

# This function gets as input the POIs visited by the user for a day and 
# uses Google Static Maps API in order to visualize the user's daily route
# on a map. The map is stored as an image.
def static_map_api(filePath, userno, day, poisVisited):
	isOK = True
	if debug:
		print("\n\nIn createMap:")
	url  = 'https://maps.googleapis.com/maps/api/staticmap?'
	url += '&size=600x300'
	url += '&maptype=roadmap'
	for poi in poisVisited:
		coord  = str(poisVisited[poi]['coordinates'].latitude) + "," 
		coord += str(poisVisited[poi]['coordinates'].longitude)
		url += '&markers=label:'
		url += str(alphabet[poi])
		url += '%7C' + coord
	url += apiKey
	
	filename = filePath + str(day) + ".png"
	
	if allow_api_calls:
		response = requests.get(url)
		if response.status_code == 403:
			isOK = False
			return isOK
		with open(filename, 'wb') as file:
		   file.write(response.content)
	else:
		if debug:
			print(url)
			print(filename)
		with open(filename, 'w') as file:
			file.write("allow_api_calls=False")
	return isOK

if __name__ == '__main__':
	# Static Map Code
	url  = 'https://maps.googleapis.com/maps/api/staticmap?'
	# url += 'center=Brooklyn+Bridge,New+York,NY'
	# url += '&zoom=13'
	url += '&size=800x600'
	url += '&maptype=roadmap'
	url += '&markers=label:A%7C33.5289425371,-112.0542503364'
	url += '&markers=label:B%7C33.55279,-112.0554'
	url += '&markers=label:C%7C33.4628408,-112.0572315'
	url += '&markers=label:D%7C33.466005,-112.221288'
	url += '&markers=label:E%7C33.5997996,-111.9869515'
	url += '&markers=label:F%7C33.4957508,-112.0300396'

	url += '&key=AIzaSyA3kg7YWugGl1lTXmAmaBGPNhDW9pEh5bo'

	response = requests.get(url)

	print(response.status_code)
	with open('hyderabad.png', 'wb') as file:
	   # writing data into the file
	   file.write(response.content)
