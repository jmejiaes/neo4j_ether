from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent / ".env")

API_KEY = os.getenv("API_KEY")

NEO4J_API_URI = os.getenv("NEO4J_URI")
NEO4J_API_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_API_PASSWORD = os.getenv("NEO4J_PASSWORD")

ETHERSCAN_API_URL = "https://api.etherscan.io/api"
