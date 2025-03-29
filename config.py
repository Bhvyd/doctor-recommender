# config.py
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch the Google API key from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
