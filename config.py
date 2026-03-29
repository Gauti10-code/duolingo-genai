import os
from dotenv import load_dotenv
 
load_dotenv()  # Load variables from .env file
 
API_KEY = os.getenv("OPENAI_API_KEY", "")
 
if not API_KEY:
    raise ValueError(
        "OpenAI API key not found. "
        "Please set OPENAI_API_KEY in your .env file or as an environment variable."
    )
