from neo4j import GraphDatabase
import os

# Load Neo4j credentials from environment variables
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_AUTH = os.getenv("NEO4J_AUTH", "neo4j/neo4jpassword").split("/")
NEO4J_USER, NEO4J_PASSWORD = NEO4J_AUTH

# Initialize Neo4j driver
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Close the driver when the application stops
def close_neo4j_driver():
    neo4j_driver.close()