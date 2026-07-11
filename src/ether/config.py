from pathlib import Path
from dotenv import load_dotenv
import os

# project root = <root>/src/ether/config.py -> parents[2]
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

API_KEY = os.getenv("API_KEY")

NEO4J_API_URI = os.getenv("NEO4J_URI")
NEO4J_API_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_API_PASSWORD = os.getenv("NEO4J_PASSWORD")

# BigQuery (primary data source — ADR-0001)
GCP_PROJECT = os.getenv("GCP_PROJECT")

# Etherscan (legacy fallback only — ADR-0001)
ETHERSCAN_API_URL = "https://api.etherscan.io/api"
