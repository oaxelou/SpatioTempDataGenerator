import my_neo4j_driver
import random
from time import sleep, time
import datetime
import requests
import json
import dicttoxml
from xml.dom.minidom import parseString

# When done:
# DONE 1) Set region randomly (now it's only East Canada)
# 2) Google Directions set API (now static so that we don't get charged)
# DONE 3) Xrisimopoiise gia tis pithanotites:
# 	import numpy
# 	numpy.random.choice(numpy.arange())

debug = False

# Auxiliary Functions

def GoogleDirectionsAPI(coordinates_origin, coordinates_destination):
	url = 'https://maps.googleapis.com/maps/api/directions/json?'
	url += 'origin=' + coordinates_origin
	url += '&destination=' + coordinates_destination
	url += '&mode=walking'
	url += '&key=AIzaSyCCDywQA7ze0vWFc8koyTJqD6MVSXm7PK8'

	response = requests.get(url)
	json_data = json.loads(response.text)

	distance = -1
	duration = -1
	if json_data['status'] == 'OK':
		distance = json_data['routes'][0]['legs'][0]['distance']['value']
		duration = json_data['routes'][0]['legs'][0]['duration']['value']
	return (distance, duration)

def getAllCategories():
	return ["Shopping Stores",
			  "Services",
			  "Religion",
			  "Supermarkets",
			  "Beauty Salons",
			  "Health & Medical",
			  "Country Clubs",
			  "Gyms",
			  "Restaurants",
			  "Bars",
			  "Cafes",
			  "Parks",
			  "Museums",
			  "Education",
			  "Entertainment"]

def getAllRegions():
	regions = {}
	regions["WestUSA"] = ["NV", "CA", "WA", "OR", "HI"]
	regions["CentralUSA"] = ["AZ", "TX", "UT", "CO", "NE"]
	regions["SouthUSA"] = ["NC", "SC", "GA", "AL", "FL", "AR"]
	regions["NorthEastUSA"] = ["PA", "NY"]
	regions["UpperMidWestUSA"] = ["OH", "WI", "IL", "MO", "MI"]
	regions["EastCanada"] = ["QC"]
	regions["CentralCanada"] = ["ON"]
	regions["WestCanada"] = ["AB", "BC", "YT", "AK"]
	return regions

def getAllCategoryPossibilities():
	# Shopping Stores, Services, Supermarkets, Health & Medical
	# Religion
	# Beauty Salons
	# Country Clubs, Gyms, Parks, Entertainment, Museums
	# Restaurants, Bars, Cafes
	# Education

	m_categ_poss = {'Shopping Stores':5.82,
					'Supermarkets':5.82,
					'Health & Medical':5.82,
					'Services':4.95,
					'Religion':3.3,
					'Beauty Salons':3.2,
					'Country Clubs':2.47,
					'Gyms':2.47,
					'Parks':2.47,
					'Entertainment':2.47,
					'Museums':2.47,
					'Restaurants':17.03,
					'Bars':17.03,
					'Cafes':17.03,
					'Education':3.5,
					'Home': 4.15}

	f_categ_poss = {'Shopping Stores':7.4,
					'Supermarkets':7.4,
					'Health & Medical':7.4,
					'Services':4.85,
					'Religion':5.9,
					'Beauty Salons':3.95,
					'Country Clubs':1.8,
					'Gyms':1.8,
					'Parks':1.8,
					'Entertainment':1.8,
					'Museums':1.8,
					'Restaurants':15.92,
					'Bars':15.92,
					'Cafes':15.92,
					'Education':3.85,
					'Home': 2.49}
	return {'m':m_categ_poss, 'f':f_categ_poss}

def getWorkingPossibilityAndDuration(education):
	workingPossibilities = {}
	workingPossibilities[0] = 82.2
	workingPossibilities[1] = 80.5
	workingPossibilities[2] = 80.7
	workingPossibilities[3] = 85
	workingPossibilities[4] = 90.5

	workingDuration = {}
	workingDuration[0] = 8.12*3600
	workingDuration[1] = 8.43*3600
	workingDuration[2] = 8.14*3600
	workingDuration[3] = 8.04*3600
	workingDuration[4] = 7.74*3600

	return (workingPossibilities[education], workingDuration[education])

def getAllEducationDegrees():
	return {0: "Less Than High School Diploma",
						1: "High School Graduates, no college",
						2: "Some college or associate degree",
						3: "Bachelor's Degree",
						4: "Advanced Degree"}

def getAllCategoryDurations(gender, age):
	f_15_24 = {'Shopping Stores':0.84*3600,
				'Supermarkets':0.84*3600,
				'Health & Medical':0.84*3600,
				'Services':0.84*3600,
				'Religion':0.2*3600,
				'Beauty Salons':0.04*3600,
				'Country Clubs':4.43*3600,
				'Gyms':4.43*3600,
				'Parks':4.43*3600,
				'Entertainment':4.43*3600,
				'Museums':4.43*3600,
				'Restaurants':1.09*3600,
				'Bars':1.09*3600,
				'Cafes':1.09*3600,
				'Education':2.64*3600,
				'Home': 1*3600}
	f_25_44 = {'Shopping Stores':0.81*3600,
				'Supermarkets':0.81*3600,
				'Health & Medical':0.81*3600,
				'Services':0.84*3600,
				'Religion':0.25*3600,
				'Beauty Salons':0.11*3600,
				'Country Clubs':3.77*3600,
				'Gyms':3.77*3600,
				'Parks':3.77*3600,
				'Entertainment':3.77*3600,
				'Museums':3.77*3600,
				'Restaurants':1.14*3600,
				'Bars':1.14*3600,
				'Cafes':1.14*3600,
				'Education':0.22*3600,
				'Home': 1.4*3600}
	f_45_64 = {'Shopping Stores':0.88*3600,
				'Supermarkets':0.88*3600,
				'Health & Medical':0.88*3600,
				'Services':0.88*3600,
				'Religion':0.36*3600,
				'Beauty Salons':0.29*3600,
				'Country Clubs':4.77*3600,
				'Gyms':0.77*3600,
				'Parks':4.77*3600,
				'Entertainment':4.77*3600,
				'Museums':4.77*3600,
				'Restaurants':1.14*3600,
				'Bars':0.3*3600,
				'Cafes':1.14*3600,
				'Education':0.1*3600,
				'Home': 2.6*3600}
	f_65plus = {'Shopping Stores':0.98*3600,
				'Supermarkets':0.98*3600,
				'Health & Medical':1.98*3600,
				'Services':0.98*3600,
				'Religion':0.61*3600,
				'Beauty Salons':0.31*3600,
				'Country Clubs':5.81*3600,
				'Gyms':0.77*3600,
				'Parks':5.81*3600,
				'Entertainment':5.81*3600,
				'Museums':5.81*3600,
				'Restaurants':1.29*3600,
				'Bars':0.29*3600,
				'Cafes':1.29*3600,
				'Education':0.02*3600,
				'Home': 4.97*3600}
	f_categ_dur = [f_15_24, f_25_44, f_45_64, f_65plus]

	m_15_24 = {'Shopping Stores':0.39*3600,
				'Supermarkets':0.39*3600,
				'Health & Medical':0.39*3600,
				'Services':0.39*3600,
				'Religion':0.09*3600,
				'Beauty Salons':0.09*3600,
				'Country Clubs':5.81*3600,
				'Gyms':5.81*3600,
				'Parks':5.81*3600,
				'Entertainment':5.81*3600,
				'Museums':5.81*3600,
				'Restaurants':1.1*3600,
				'Bars':1.1*3600,
				'Cafes':1.1*3600,
				'Education':2.08*3600,
				'Home': 1*3600}
	m_25_44 = {'Shopping Stores':0.52*3600,
				'Supermarkets':0.52*3600,
				'Health & Medical':0.52*3600,
				'Services':0.52*3600,
				'Religion':0.2*3600,
				'Beauty Salons':0.12*3600,
				'Country Clubs':2.51*3600,
				'Gyms':1.51*3600,
				'Parks':2.51*3600,
				'Entertainment':2.51*3600,
				'Museums':2.51*3600,
				'Restaurants':1.2*3600,
				'Bars':1.2*3600,
				'Cafes':1.2*3600,
				'Education':0.23*3600,
				'Home': 1.2*3600}
	m_45_64 = {'Shopping Stores':1.39*3600,
				'Supermarkets':1.39*3600,
				'Health & Medical':1.39*3600,
				'Services':1.39*3600,
				'Religion':0.26*3600,
				'Beauty Salons':0.18*3600,
				'Country Clubs':3.1*3600,
				'Gyms':0.51*3600,
				'Parks':3.1*3600,
				'Entertainment':3.1*3600,
				'Museums':3.1*3600,
				'Restaurants':1.22*3600,
				'Bars':1.2*3600,
				'Cafes':1.22*3600,
				'Education':0.11*3600,
				'Home': 2.8*3600}
	m_65plus = {'Shopping Stores':0.85*3600,
				'Supermarkets':0.85*3600,
				'Health & Medical':0.85*3600,
				'Services':0.85*3600,
				'Religion':0.45*3600,
				'Beauty Salons':0.24*3600,
				'Country Clubs':5.94*3600,
				'Gyms':0.25*3600,
				'Parks':5.94*3600,
				'Entertainment':5.94*3600,
				'Museums':5.94*3600,
				'Restaurants':1.36*3600,
				'Bars':0.2*3600,
				'Cafes':1.36*3600,
				'Education':0.03*3600,
				'Home': 5*3600}
	m_categ_dur = [m_15_24, m_25_44, m_45_64, m_65plus]

	if gender == 'f':
		if   age < 25:return f_15_24
		elif age < 45:return f_25_44
		elif age < 65:return f_45_64
		else: return f_65plus
	else:
		if   age < 25:return m_15_24
		elif age < 45:return m_25_44
		elif age < 65:return m_45_64
		else: return m_65plus

def findPossibilitiesFromProfile(categories, userProfile):
	# Get the user's profile
	(age, gender, education) = userProfile
	
	categPossibilities = getAllCategoryPossibilities()
	meanCheckInDur = getAllCategoryDurations(gender, age)

	if debug:
		print(meanCheckInDur)
	
	return (categPossibilities[gender], meanCheckInDur)

def setup_user_profil(categories, regions):
	# Constants
	EducationDegrees = getAllEducationDegrees()
	
	# Set Randomly the User's Profil
	gender = random.choice(['m', 'f'])
	age = random.randint(18, 90)
	education = random.choice(list(EducationDegrees))
	userProfile = (age, gender, education)
	if debug:
		print("Age:", age, " - Gender:", gender, " - Education:", education)

	(categPossibilities, meanCheckInDur) = findPossibilitiesFromProfile(categories, userProfile)
		
	# Home
	home, region = my_neo4j_driver.neo4j_find_random_poi(regions)
	if debug:
		print("Home: ", home['name'])

	# Work
	workingPossibility, workingDuration = getWorkingPossibilityAndDuration(education)
	isWorking = random.choices([True, False], [workingPossibility, 100-workingPossibility])
	workPlace = None
	if isWorking: (workPlace, _) = my_neo4j_driver.neo4j_find_random_poi(regions, region)
	work = (isWorking, workPlace, workingDuration)
	if debug: 
		print("is working?", isWorking, " - workPlace:", workPlace, " - workingDuration:", workingDuration)

	return (userProfile, home, region, work, categPossibilities, meanCheckInDur)

# Main Functions

def findTrajectoryPerDay(categories, regions, input_consts, input_vars):
	# debug = False
		
	# Constants to use
	(maxDist, startTime, endTime, chkNum, stdDevCheckIn) = input_consts
	
	# Variables to use
	(home, work, region, poisInRange, categPossibilities, meanCheckInDur) = input_vars
	(isWorking, workPlace, workingDur) = work

	# The final sets of POIs and times (check in, check out & duration)
	poisVisited = {} # The pois that the user visited in the same day
	purpose = {} # The purpose of visit to each POI
	checkInTimes = {} # All the check in timestamps in the day
	checkOutTimes = {} # All the check out timestamps in the day
	transportDurations = {} # All the durations of movement in the day
	categoriesVisited = []

	# Initializations of temp variables
	duration = 0    # The duration of the trajectory to the POI (sec)
	checkInDur = 0  # The duration the user spent in a POI (sec)
	checkInTime = 0 # The NON-relative time in the day when the check in starts (sec)
	checkOutTime = 0 # The NON-relative time in the day when the check in ends (sec)
	timeBefore = 0 # The time before the user begins to visit the POI (sec)

	if debug:
		print("\nGoing to create trajectory now!!")

	##################################################
	# Step 1: First POI of the day

	# poisVisited[0] = home
	p = home
	# poisInRange.remove(p)
	timeBefore = startTime

	##################################################
	# Step 2: Rest of POIs of the day
	if debug:
		print("keys:")
		print(list(categPossibilities.keys()))
		print("values:")
		print(list(categPossibilities.values()))
		print(isWorking)
		print(workPlace)
	if isWorking:
		predictedTrajectory = random.choices(list(categPossibilities.keys()), list(categPossibilities.values()), k=chkNum-1)
		maxChkNum = chkNum-1
	else:
		predictedTrajectory = random.choices(list(categPossibilities.keys()), list(categPossibilities.values()), k=chkNum)
		maxChkNum = chkNum
	if debug:
		print("predictedTrajectory")
		print(predictedTrajectory)
	for i in range(maxChkNum):
		if debug:
			sleep(0.5)
		if not p: break

		# Get all poisInRange & Find new POI:
		if not poisInRange: break
		newP = None

		if isWorking and i == 0:
			currentCategory = "Work"
		else:
			currentCategory = predictedTrajectory[i-1]
		if debug:
			print("\nGoing to search for category:", currentCategory)
			print("Categories:", categPossibilities)
		
		if currentCategory == "Work":
			newP = workPlace
			if debug:print("Selected workPlace:", workPlace)
		elif currentCategory == "Home":
			newP = home
			if debug:print("Selected home:", home)
		else:
			for poi in poisInRange:
				if currentCategory in poi['categories']:
					newP = poi
					break
		
		if not newP:
			if debug:print("RANDOM POI!!!!!!!!!!!")
			newP = random.choice(poisInRange)

		if debug:
			print("\n", str(i), ": ", newP['name'], " - ", newP['categories'])
		# Find checkOutTime:
		# Get distance & duration from p to newP (google maps directions API)
		googleDirections_P_str = str(p['coordinates'].latitude) + "," + str(p['coordinates'].longitude)
		googleDirections_NewP_str = str(newP['coordinates'].latitude) + "," + str(newP['coordinates'].longitude)
		duration = 20
		# (_, duration) = GoogleDirectionsAPI(googleDirections_P_str,googleDirections_NewP_str)
		if currentCategory == "Work":
			if debug:print("\nWORK ", workingDur)
			while True:
				checkInDur = int(random.gauss(workingDur, stdDevCheckIn))
				if checkInDur > 0:
					break
		elif currentCategory == "Home":
			if debug:print("\nhome ", workingDur/8)
			while True:
				checkInDur = int(random.gauss(workingDur, stdDevCheckIn))
				if checkInDur > 0:
					break
		else:
			while True:
				checkInDur = int(random.gauss(meanCheckInDur[currentCategory], stdDevCheckIn))
				if checkInDur > 0:
					break
		checkInTime = timeBefore + duration
		checkOutTime = timeBefore + duration + checkInDur
		if checkOutTime > endTime: 
			if debug:
				print("Exceeded the end of the day. Going to discard it.\n")
			break

		if debug:
			print("\ttimeBefore:", timeBefore, "(sec) = ", str(datetime.timedelta(seconds=timeBefore)), " o'clock")
			print("\t+ duration:", duration, "(sec) = ", str(datetime.timedelta(seconds=duration)), "o'clock")
			print("\t+ checkInDur:", checkInDur, "(sec) = ",str(datetime.timedelta(seconds=checkInDur)), "o'clock")
			print("\t= checkOutTime: ", checkOutTime, "(sec) = ", str(datetime.timedelta(seconds=checkOutTime)), "o'clock")
		# Get variables ready for the next iteration
		timeBefore = checkOutTime
		poisVisited[i] = newP
		purpose[i] = currentCategory
		checkInTimes[i] = checkInTime
		checkOutTimes[i] = checkOutTime
		transportDurations[i] = duration
		if debug:
			print("categories: ", newP['categories'])
			for categ in newP['categories']:
				if categ not in categoriesVisited:categoriesVisited.append(categ)
			print(categoriesVisited)
		p = newP
		if p in poisInRange:
			poisInRange.remove(p)

	##################################################
	# Step 3: Sum up of the trajectory - Maps Static API

	if debug:
		print("\n\nStep 3: Sum up of the trajectory:")
		sleep(1)

		print("\tAll the POIs that were visited:")
		for i in range(len(poisVisited)):
			print(str(datetime.timedelta(seconds=checkInTimes[i])), "o'clock", "\t - ", str(datetime.timedelta(seconds=checkOutTimes[i])), "o'clock", "\t : ", poisVisited[i]['name'], " - ", poisVisited[i]['categories'])

		print("\tAll the durations that were visited:")
		for i in range(len(poisVisited)):
			print(str(datetime.timedelta(seconds=transportDurations[i])))

	# print("\tGoing to create the Static Map now.")

	return (poisVisited, purpose, checkInTimes, checkOutTimes, transportDurations)

def generate_trajectories_per_user(categories, regions, input_consts, user_no, time_period, json_file):
	# Variables 
	(userProfile, home, region, work, categPossibilities, meanCheckInDur) = setup_user_profil(categories, regions)
	
	poisInRange = my_neo4j_driver.neo4j_find_POIs_in_range(home, input_consts[0], region)
	
	input_vars = (home, work, region, poisInRange, categPossibilities, meanCheckInDur)
	
	poisVisited = {}
	purpose = {}
	checkInTimes = {}
	checkOutTimes = {}
	durations = {}

	# with open('dataset.xml', 'w') as xml_file:
	# userStr = "user_no:" + str(user_no)
	userDict = {"user":str(user_no)}
	userDict["days"] = {} 
	# print("- User: ", user_no)
	if debug:
		print(userDict)
	
	for day in range(time_period):
		(poisVisited[day], purpose[day], checkInTimes[day], checkOutTimes[day], durations[day]) = findTrajectoryPerDay(categories, regions, input_consts, input_vars)

		userDict["days"][day] = {}
		if debug:
			print("- Day", day)
			print("number of pois: ", len(poisVisited[day]))
			print(userDict['days'])
		for i in range(len(poisVisited[day])):
			# POIstr  = str(datetime.timedelta(seconds=checkInTimes[day][i]))  + "o'clock" + "\t - "
			# POIstr += str(datetime.timedelta(seconds=checkOutTimes[day][i])) + "o'clock" + "\t - Action: "
			# POIstr += purpose[day][i] + "\t : "
			# POIstr += poisVisited[day][i]['name']
			# print(POIstr)
			userDict["days"][day][i] = {}
			userDict["days"][day][i]["POI number"] = str(day)
			userDict["days"][day][i]["checkin"] = checkInTimes[day][i]
			userDict["days"][day][i]["checkout"] = checkOutTimes[day][i]
			userDict["days"][day][i]["purpose"] = purpose[day][i]
			userDict["days"][day][i]["POI"] = {}

			userDict["days"][day][i]["POI"]['name'] = poisVisited[day][i]['name']
			userDict["days"][day][i]["POI"]['business_id'] = poisVisited[day][i]['business_id']
			userDict["days"][day][i]["POI"]['state'] = poisVisited[day][i]['state']
			userDict["days"][day][i]["POI"]['postal_code'] = poisVisited[day][i]['postal_code']
			userDict["days"][day][i]["POI"]['city'] = poisVisited[day][i]['city']
			userDict["days"][day][i]["POI"]['address'] = poisVisited[day][i]['address']
			userDict["days"][day][i]["POI"]['coordinates'] = poisVisited[day][i]['coordinates']
			userDict["days"][day][i]["POI"]['categories'] = poisVisited[day][i]['categories']
			if debug:
				print(userDict['days'][day][i])


			# xml_file.write(POIxml)
			# print(parseString(POIxml.decode('utf-8')).toprettyxml())
			# xml_file.write("\n")
			# print("\n")
			# print(str(datetime.timedelta(seconds=checkInTimes[day][i])), "o'clock", "\t - ", str(datetime.timedelta(seconds=checkOutTimes[day][i])), "o'clock", "\t - Action: " , purpose[day][i], "\t\t : ", poisVisited[day][i]['name'], " - ", poisVisited[day][i]['categories'])

	# print(userDict)
	userJSON = json.dumps(userDict)
	json_file.write(userJSON+"\n")
	# userXML = dicttoxml.dicttoxml(userDict, attr_type=False)
	# xml_file.write(userXML.decode('utf-8')+"\n")
	# print("\tAll the durations that were visited:")
	# for i in range(1, len(poisVisited[day])):
	# 	print(str(datetime.timedelta(seconds=durations[day][i])))

	# print("Done")

def data_generator():
	# The final categories are going to be used later on
	final_categories = getAllCategories()
	regions = getAllRegions()

	# Set the constants
	maxDist = 20000 # The max distance a user can go from his home
	startTime = 28800 # = 8:00 When the user starts visiting places (sec)
	endTime = 79200 # = 22:00 The end of the day (sec)
	chkNum = 10 # The max number of checkins 
	stdDevCheckIn = 3600 # 1 hour standard deviation
	DAYSPER = {'month':30, 'week':7, 'day':1}
	time_period = DAYSPER['month']
	NumberOfUsers = 100
	input_consts = (maxDist, startTime, endTime, chkNum, stdDevCheckIn)
	
	with open('dataset.json', 'w', encoding='utf-8') as json_file:
		for user_no in range(NumberOfUsers):
			generate_trajectories_per_user(final_categories, regions, input_consts, user_no, time_period, json_file)
	print("Done")
if __name__ == '__main__':
	start_time = time()
	data_generator()
	print("--- %s seconds ---" % (time() - start_time))