from watson_developer_cloud import ToneAnalyzerV3
from config import TONEANALYZER_API_KEY, TONEANALYZER_API_URL, TONEANALYZER_API_VER
import json

# :sample return:
# {
#   "document_tone": {
#     "tones": [
#       {
#         "score": 0.880435,
#         "tone_id": "joy",
#         "tone_name": "Joy"
#       }
#     ]
#   }
# }


tone_analyzer = ToneAnalyzerV3(
    version=TONEANALYZER_API_VER,
    iam_apikey=TONEANALYZER_API_KEY,
    url=TONEANALYZER_API_URL
)

text = 'thank you'

tone_analysis = tone_analyzer.tone(
    {'text': text},
    'application/json'
).get_result()
print(json.dumps(tone_analysis, indent=2))
