from neo4j import GraphDatabase
import random

# add try block here
driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "12345"))
print("Connected to the db")

def __find_random_POI__(tx, region):
	# print("Going to search for a POI in", region)
	query_str  = "match (n:" + region + ") with n, rand() as rand_num "
	query_str += "return n order by rand_num limit 1;"
	# query_str  = "match (n:" + region + ") "
	# query_str += "return n limit 1;"
	result = tx.run(query_str)
	for record in result:
		home = record['n']
		break # there is only one result anyways
	# print(home)
	# for k in home:
	# 	print(k, ": ", home[k])
	return home

def neo4j_find_random_poi(regions, region=None):
	if not region:
		region = random.choice(list(regions.keys()))
		# region = "EastCanada"
		print("Just chose ", region)
	# else:
	# 	print("Did not choose ", region)
	randomPOI = None
	with driver.session() as session:
		randomPOI = session.write_transaction(__find_random_POI__, region)
	# if randomPOI:
	# 	print(randomPOI['name'])
	# else:
	# 	print("No random POI could be found.")
	return randomPOI, region

def __find_POIs_in_range__(tx, centralPOI, radius, region):
	# print("Going to search for POIs in range of " + str(radius) + " for POI: ", centralPOI)
	query_str  = "match (n:" + region + "), (m:" + region + ") " 
	query_str += "where n.business_id='" + centralPOI['business_id'] + "' and n <> m "
	query_str += "and distance(n.coordinates, m.coordinates) < " + str(radius) + " return m;"
	result = tx.run(query_str)
	pois = []
	for record in result:
		pois.append(record['m'])
	# print("In aux: ", str(len(pois)))
	# return {i : pois[i-1] for i in range(1, len(pois)+1)}
	return pois

def neo4j_find_POIs_in_range(centralPOI, radius, region):
	# print("Going to find POIs in range of " + str(radius) + " for POI: ", centralPOI)
	pois_in_range = None
	with driver.session() as session:
		pois_in_range = session.write_transaction(__find_POIs_in_range__, centralPOI, radius, region)
	# if pois_in_range:
	# 	print("The number of POIs is: ", str(len(pois_in_range)))
	# else:
	# 	print("No pois in range where found")
	return pois_in_range

def neo4j_close_connection():
	driver.close()

if __name__ == '__main__':
	region = "EastCanada"
	# print("Just chose ", region)
	randomPOI = None
	with driver.session() as session:
		randomPOI = session.write_transaction(__find_random_POI__, region)

	print(randomPOI['coordinates'].latitude, ",", randomPOI['coordinates'].longitude)