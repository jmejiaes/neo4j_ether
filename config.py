from dotenv import load_dotenv
import os

# load the .env file
load_dotenv() 

# get the API key from the .env file
API_KEY = os.getenv("API_KEY")

# get the neo4j API key from the .env file
NEO4J_API_URI = os.getenv("NEO4J_URI")
NEO4J_API_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_API_PASSWORD = os.getenv("NEO4J_PASSWORD")


# set the etherscan API URL
ETHERSCAN_API_URL = "https://api.etherscan.io/api"