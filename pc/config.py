import os
from dotenv import load_dotenv

load_dotenv()

TONEANALYZER_API_KEY = os.getenv('TONEANALYZER_API_KEY')
TONEANALYZER_API_URL = os.getenv('TONEANALYZER_API_URL')
TONEANALYZER_API_VER = os.getenv('TONEANALYZER_API_VER')

SEMANTICS_API_KEY = os.getenv('SEMANTICS_API_KEY')
SEMANTICS_API_URL = os.getenv('SEMANTICS_API_URL')
SEMANTICS_API_VER = os.getenv('SEMANTICS_API_VER')

SUTIME_JARS = os.path.join(os.path.dirname(__file__), 'jars')
