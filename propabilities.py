#!/usr/bin/env python3.9

# Axelou Olympia, December 2020
# Greece, University of Thessaly, dpt. Electrical & Computer Engineering
#
# Project: Spatio-temporal and spatio-textual data generator
# Supervisor: Vassilakopoulos Michail
#
# This file consists of auxiliary functions that aid in the 
# connection between the main code and the Google Maps API. In particular,
# Google Directions API and Google Static Map API.
#
# Example of usage:
# >$ python propabilities.py -U 2000 -s 8000
# The above command specifies that the script will run for 2000 users and 
# that the users' IDs will be in the range [8000, 10000) 

import my_neo4j_driver
import my_google_maps_api
import random
from time import sleep, time
import datetime
import requests
import json
import dicttoxml
from xml.dom.minidom import parseString
import os
import errno
import argparse

debug = False
result_folder = "final_dataset/"

if not os.path.exists(os.path.dirname(result_folder)):
    try:
        os.makedirs(os.path.dirname(result_folder))
    except OSError as exception:
        raise
if not os.path.exists(os.path.dirname(result_folder+"images/")):
    try:
        os.makedirs(os.path.dirname(result_folder+"images/"))
    except OSError as exception:
        raise

# # # # # # # # # # Code for the arguments # # # # # # # # # # 

def positive_int(value):
    try:
        value = int(value)
        if value <= 0:
            raise argparse.ArgumentTypeError("{} is not a positive integer".format(value))
    except ValueError:
        raise argparse.ArgumentTypeError("{} is not an integer".format(value))
    return value

def positive_float(value):
    try:
        value = float(value)
        if value <= 0:
            raise argparse.ArgumentTypeError("{} is not a positive decimal".format(value))
    except ValueError:
        raise argparse.ArgumentTypeError("{} is not a decimal".format(value))
    return value

def non_negative_int(value):
    try:
        value = int(value)
        if value < 0:
            raise argparse.ArgumentTypeError("{} is not a positive integer".format(value))
    except ValueError:
        raise argparse.ArgumentTypeError("{} is not an integer".format(value))
    return value

parser = argparse.ArgumentParser()
helpString = "The maximum distance of a POI from home (positive integer, in meters)"
parser.add_argument("-M", "--maxDistance", help=helpString, type=positive_int)
helpString = "The start of the day (positive integer, in seconds from time 00:00)"
parser.add_argument("-S", "--startTime", help=helpString, type=positive_int)
helpString  = "The end of the day (positive integer, in seconds from time 00:00)"
parser.add_argument("-E", "--endTime", help=helpString, type=positive_int)
helpString  = "The maximum number of check-ins per day per user"
helpString += "(positive integer)"
parser.add_argument("-C", "--checkInNum", help=helpString, type=positive_int)
helpString  = "The standard deviation for the normal distribution of the"
helpString += " check-ins' duration (positive number)"
parser.add_argument("-D", "--stdDev", help=helpString, type=positive_float)
helpString  = "The period of time for which the generator will produce"
helpString +=" daily routes (positive integer, in days)"
parser.add_argument("-T", "--timePeriod", help=helpString, type=positive_int)
helpString  = "The number of virtual users that will be generated."
helpString += "(integer, positive)"
parser.add_argument("-U", "--usersNum", help=helpString, type=positive_int)
helpString  = "The starting ID of virtual users that will be generated "
helpString += "(integer, non-negative)"
parser.add_argument("-s", "--startUserNum", help=helpString, type=non_negative_int)
helpString  = "The ending ID of virtual users that will be generated."
helpString += " If -s is not specified then this argument will be ignored."
helpString += " Also, this argument has to be an integer larger than -s "
helpString += "(integer, non-negative)"
parser.add_argument("-e", "--endUserNum", help=helpString, type=non_negative_int)

# # # # # # # # # # End of code for the arguments # # # # # # # # # # 

# # # # # # # # # # Auxiliary Functions # # # # # # # # # #

# This function returns all possible categories of the POIs available
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

# This function returns a dictionary with all the regions as key and
# as value a list with all the states that are in the corresponding region
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

# This function returns in a dictionary the possibilities for each
# POI category for both genders male and female.
# As examined in statistical surveys, some categories seemed to be 
# chosen in the same frequency by the people. The categorization is as follows:
# {Shopping Stores, Services, Supermarkets, Health & Medical}
# {Religion}
# {Beauty Salons}
# {Country Clubs, Gyms, Parks, Entertainment, Museums}
# {Restaurants, Bars, Cafes}
# {Education}
# Lastly, there is the category "Home" which was indirectly derived from the surveys
def getAllCategoryPossibilities():
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

# This function returns the possibility of a person to work 
# and the mean duration of it for the given level of the person's education
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

# This function returns a dictionary with all the levels of education
def getAllEducationDegrees():
	return {0: "Less Than High School Diploma",
			1: "High School Graduates, no college",
			2: "Some college or associate degree",
			3: "Bachelor's Degree",
			4: "Advanced Degree"}

# This function returns the duration of each category of activity
# for the given gender and age, based on surveys
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

# This function gets as input the profile of the virtual user 
# and it returns the possibilities and the mean durations for each category
def findPossibilitiesFromProfile(userProfile):
	# Get the user's profile
	(age, gender, education) = userProfile
	
	categPossibilities = getAllCategoryPossibilities()
	meanCheckInDur = getAllCategoryDurations(gender, age)

	if debug:
		print(meanCheckInDur)
	
	return (categPossibilities[gender], meanCheckInDur)

# # # # # # # # # # End of Auxiliary Functions # # # # # # # # # #

# # # # # # # # # # Main Functions # # # # # # # # # #

# This function gets as input all regions.
# It randomly sets the user's profile (gender, age and education level),
# and uses other aux functions to find the possibilities and the durations
# of the categories.
# Also, it performs a query in the Neo4j database to randomly set the Home,
# finds the possibility for the given profile to work and sets a random POI
# of the Neo4j database to be the workplace of the user.
# It returns the possibilities and the durations, home and workplace.
def setup_user_profil(regions):
	# Constants
	EducationDegrees = getAllEducationDegrees()
	
	# Set Randomly the User's Profil
	gender = random.choice(['m', 'f'])
	age = random.randint(18, 90)
	education = random.choice(list(EducationDegrees))
	userProfile = (age, gender, education)
	if debug:
		print("Age:", age, " - Gender:", gender, " - Education:", education)

	(categPossibilities, meanCheckInDur) = findPossibilitiesFromProfile(userProfile)
		
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

# This function creates the daily trajectory of a user
# It takes as input the categories of activities, 
# some constants set by the programmer (e.g. max distance, number of check-ins)
# and some variables for the current user like home and workplace, 
# the regions he's in, the POIs around his home etc...
# It returns the detailed trajectory (places visited, check-in & transport durations)
def findTrajectoryPerDay(categories, input_consts, input_vars):
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
	transportDistances = {} # All the distances of movement in the day
	# categoriesVisited = []

	# Initializations of temp variables
	duration = 0    # The duration of the trajectory to the POI (sec)
	distance = 0    # The distance of the trajectory to the POI (m)
	checkInDur = 0  # The duration the user spent in a POI (sec)
	checkInTime = 0 # The NON-relative time in the day when the check in starts (sec)
	checkOutTime = 0 # The NON-relative time in the day when the check in ends (sec)
	timeBefore = 0 # The time before the user begins to visit the POI (sec)

	if debug:
		print("\nGoing to create trajectory now!!")

	##################################################
	# Step 1: Set home

	p = home
	timeBefore = startTime

	##################################################
	# Step 2: Find the trajectory of the day
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
			if debug:
				print("Selected workPlace:", workPlace)
		elif currentCategory == "Home":
			newP = home
			if debug:
				print("Selected home:", home)
		else:
			for poi in poisInRange:
				if currentCategory in poi['categories']:
					newP = poi
					break
		
		if not newP:
			if debug:
				print("Didn't find a poi of this category. Going to choose one randomly.")
			newP = random.choice(poisInRange)

		if debug:
			print("\n", str(i), ": ", newP['name'], " - ", newP['categories'])
		
		# Find checkOutTime:
		# Get distance & duration from p to newP (google maps directions API)
		coordinates_P = str(p['coordinates'].latitude) + "," + str(p['coordinates'].longitude)
		coordinates_newP = str(newP['coordinates'].latitude) + "," + str(newP['coordinates'].longitude)
		(distance, duration) = my_google_maps_api.google_directions_api(coordinates_P,coordinates_newP)
		if currentCategory == "Work":
			if debug:
				print("\nWORK ", workingDur)
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
		transportDistances[i] = distance
		# if debug:
		# 	print("categories: ", newP['categories'])
		# for categ in newP['categories']:
		# 	if categ not in categoriesVisited:categoriesVisited.append(categ)
		# print(categoriesVisited)
		p = newP
		if p in poisInRange:
			poisInRange.remove(p)

	##################################################
	# Step 3: Sum up of the trajectory - Maps Static API

	# APOFASISE AN THA BRISKEI TO STATIC MAP EDW H OXI

	if debug:
		print("\n\nStep 3: Sum up of the trajectory:")
		sleep(1)
		print("\tAll the POIs that were visited:")
		for i in range(len(poisVisited)):
			print(str(datetime.timedelta(seconds=checkInTimes[i])), "o'clock", "\t - ", str(datetime.timedelta(seconds=checkOutTimes[i])), "o'clock", "\t : ", poisVisited[i]['name'], " - ", poisVisited[i]['categories'])
		print("\tAll the durations that were visited:")
		for i in range(len(poisVisited)):
			print(str(datetime.timedelta(seconds=transportDurations[i])))

	return (poisVisited, purpose, checkInTimes, checkOutTimes, transportDurations, transportDistances)


def generate_trajectories_per_user(categories, regions, input_consts, user_no, time_period, json_file):
	# Variables 
	(userProfile, home, region, work, categPossibilities, meanCheckInDur) = setup_user_profil(regions)
	
	poisInRange = my_neo4j_driver.neo4j_find_POIs_in_range(home, input_consts[0], region)
	
	input_vars = (home, work, region, poisInRange, categPossibilities, meanCheckInDur)
	
	poisVisited = {}
	purpose = {}
	checkInTimes = {}
	checkOutTimes = {}
	transportDurations = {}
	transportDistances = {}

	userDict = {"user":str(user_no)}
	userDict["days"] = {} 
	if debug:
		print(userDict)
	
	for day in range(time_period):
		(poisVisited, purpose, checkInTimes, checkOutTimes, transportDurations, transportDistances) = findTrajectoryPerDay(categories, input_consts, input_vars)

		userDict["days"][day] = {}
		userDict["days"][day]["total_pois_visited"]=len(poisVisited)
		userDict["days"][day]["pois_visited"]={}

		if debug:
			print("- Day", day)
			print("number of pois: ", len(poisVisited))
			print(userDict['days'])
		for poi in range(len(poisVisited)):
			userDict["days"][day]["pois_visited"][poi] = {}
			userDict["days"][day]["pois_visited"][poi]["transport_duration"] = transportDurations[poi]
			userDict["days"][day]["pois_visited"][poi]["transport_distance"] = transportDistances[poi]
			userDict["days"][day]["pois_visited"][poi]["checkin"] = checkInTimes[poi]
			userDict["days"][day]["pois_visited"][poi]["checkout"] = checkOutTimes[poi]
			userDict["days"][day]["pois_visited"][poi]["purpose"] = purpose[poi]
			userDict["days"][day]["pois_visited"][poi]["business_details"] = {}

			userDict["days"][day]["pois_visited"][poi]["business_details"]['name'] = poisVisited[poi]['name']
			userDict["days"][day]["pois_visited"][poi]["business_details"]['business_id'] = poisVisited[poi]['business_id']
			userDict["days"][day]["pois_visited"][poi]["business_details"]['state'] = poisVisited[poi]['state']
			userDict["days"][day]["pois_visited"][poi]["business_details"]['postal_code'] = poisVisited[poi]['postal_code']
			userDict["days"][day]["pois_visited"][poi]["business_details"]['city'] = poisVisited[poi]['city']
			userDict["days"][day]["pois_visited"][poi]["business_details"]['address'] = poisVisited[poi]['address']
			userDict["days"][day]["pois_visited"][poi]["business_details"]['coordinates'] = poisVisited[poi]['coordinates']
			userDict["days"][day]["pois_visited"][poi]["business_details"]['categories'] = poisVisited[poi]['categories']
			if debug:
				print(userDict['days'][day]["pois_visited"][poi])
				print(poisVisited[poi]['name'], ":", str(poisVisited[poi]['coordinates'].latitude) + "," + str(str(poisVisited[poi]['coordinates'].longitude)))
		my_google_maps_api.static_map_api(str(result_folder+"images/staticmap_"), user_no, day, poisVisited) # pois visited this day.
	userJSON = json.dumps(userDict)
	json_file.write(userJSON+"\n")

def data_generator():
	# The final categories are going to be used later on
	final_categories = getAllCategories()
	regions = getAllRegions()

	# Get the arguments 
	args = parser.parse_args()
	if args.endUserNum and not args.startUserNum:
		print("Must also set --startUserNum parameter with --endUserNum")
		exit()
	elif args.endUserNum and args.startUserNum and args.startUserNum > args.endUserNum:
		print("User's start number must be smaller than or equal to the end number.")
		exit()

	# Set the constants
	DAYSPER           = {'2months':60, 'month':30, 'week':7, 'day':1}
	DEFAULT_MAXDIST   = 20000 # The max distance a user can go from his home
	DEFAULT_STARTTIME = 28800 # = 8:00 When the user starts visiting places (sec)
	DEFAULT_ENDTTIME  = 79200 # = 22:00 The end of the day (sec)
	DEFAULT_CHKINNUM  = 10 # The max number of checkins 
	DEFAULT_STDDEV    = 3600 # 1 hour standard deviation
	DEFAULT_USERSNUM  = 50

	maxDist       = args.maxDistance  if args.maxDistance  else DEFAULT_MAXDIST
	startTime     = args.startTime    if args.startTime    else DEFAULT_STARTTIME
	endTime       = args.endTime      if args.endTime      else DEFAULT_ENDTTIME
	chkNum        = args.checkInNum   if args.checkInNum   else DEFAULT_CHKINNUM
	stdDevCheckIn = args.stdDev       if args.stdDev       else DEFAULT_STDDEV
	numberOfUsers = args.usersNum     if args.usersNum     else DEFAULT_USERSNUM
	time_period   = args.timePeriod   if args.timePeriod   else DAYSPER['2months']
	startUser     = args.startUserNum if args.startUserNum else 0
	endUser       = args.endUserNum   if args.endUserNum   else startUser+numberOfUsers

	print(maxDist)
	print(startTime)
	print(endTime)
	print(chkNum)
	print(stdDevCheckIn)
	print(time_period)
	print(numberOfUsers)
	print(startUser)
	print(endUser)
	exit()
	
	input_consts  = (maxDist, startTime, endTime, chkNum, stdDevCheckIn)
	
	json_fle = "dataset_" + str(startUser) + "_" + str(endUser) + ".json"
	with open(result_folder + json_fle, 'w', encoding='utf-8') as json_file:
		for user_no in range(startUser, endUser):
			generate_trajectories_per_user(final_categories, regions, input_consts, user_no, time_period, json_file)
			if user_no % 10 == 0:print("user:", user_no)
	print("Done")

# # # # # # # # # # End of Main Functions # # # # # # # # # #

if __name__ == '__main__':
	start_time = time()
	data_generator()
	print("--- %s seconds ---" % (time() - start_time))

