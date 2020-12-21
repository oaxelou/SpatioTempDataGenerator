# SpatioTempDataGenerator
A realistic Spatio-Textual and Spatio-Temporal Data Generator.

It's a python project that uses a Neo4j Graph Database to store the POIs used by

Additional databases/APIs used:
- Neo4j Database connection 
- Google Directions API & Google Static Maps API (an API key needed for this code to run)

Additional libraries needed for this project:
- neo4j==4.1.1
- requests==2.24.0

Before running this code, the data must have been entered in the Neo4j database. The create queries are in the neo4j_scripts/create_queries/ folder. The POIs (Point Of Interest) used have been divided into regions (clusters larger than states).
