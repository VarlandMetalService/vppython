# Load environment variables.
from dotenv import load_dotenv
load_dotenv()

# Load package classes.
from .config import Config

# Create global config object.
global_config = Config()