
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

MODEL_NAME = "gemini-3.1-flash-lite"

MAX_WEBPAGE_CALLS = 3
MAX_SEARCH_RESULTS = 5
MAX_WEBPAGE_CHARACTERS = 12000

REQUEST_TIMEOUT = 15
