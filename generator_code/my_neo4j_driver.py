# Axelou Olympia, December 2020
# Greece, University of Thessaly, dpt. Electrical & Computer Engineering
#
# Project: Spatio-temporal and spatio-textual data generator
# Supervisor: Vassilakopoulos Michail
#
# This file consists of auxiliary scripts and functions that aid in the 
# connection between the main code and the Neo4j database.

from neo4j import GraphDatabase, READ_ACCESS
from time import time
import random

debug=False

try:
	driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "12345"))
except Exception as e:
	print("Problem connecting to Neo4j database.")
	exit()

if debug:
	print("Connected to the db")

# This function has a double purpose:
# 1) It can be used to randomly set the workplace of a user.
#    To do that, the second parameter must be set to a valid region
# 2) It can be used to randomly set the home of a user.
#    For this option, the second parameter should not be set. This is because
#    this function also randomly chooses the region of the user's home
def neo4j_find_random_poi(regions, region=None):
	if not region:
		region = random.choice(list(regions.keys()))
		if debug:
			print("Just chose ", region)
	randomPOI = None
	with driver.session(default_access_mode=READ_ACCESS) as session:
		query_str  = "match (n:" + region + ") with n, rand() as rand_num "
		query_str += "return n order by rand_num limit 1;"
		result = session.run(query_str)
		for record in result:
			home = record['n']
			randomPOI = home
			break # there is only one result anyways
	return randomPOI, region

# This function finds all POIs of a specific region that are around 
# a centralPOI set by the 1st parameter and inside the imaginary circle 
# with radius the 2nd parameter of the function. 
def neo4j_find_POIs_in_range(centralPOI, radius, region):
	pois_in_range = None
	with driver.session(default_access_mode=READ_ACCESS) as session:
		query_str  = "match (n:" + region + "), (m:" + region + ") " 
		query_str += "where n.business_id='" + centralPOI['business_id'] + "' and n <> m "
		query_str += "and distance(n.coordinates, m.coordinates) < " + str(radius) + " return m;"
		result = session.run(query_str)
		pois_in_range = []
		for record in result:
			pois_in_range.append(record['m'])
	return pois_in_range

def neo4j_close_connection():
	driver.close()

if __name__ == '__main__':
	region = "EastCanada"
	
	start_time = time()
	randomPOI,_ = neo4j_find_random_poi(None, region)
	print(randomPOI['coordinates'].latitude, ",", randomPOI['coordinates'].longitude)
	print("--- %s seconds ---" % (time() - start_time))

