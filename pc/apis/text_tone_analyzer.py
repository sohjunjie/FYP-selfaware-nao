from watson_developer_cloud import ToneAnalyzerV3
from config import TONEANALYZER_API_KEY, TONEANALYZER_API_URL, TONEANALYZER_API_VER
import json

"""
demo: https://tone-analyzer-demo.ng.bluemix.net/

"""

class ToneAnalyzer():

    def __init__(self):
        self.tone_analyzer = ToneAnalyzerV3(
            version=TONEANALYZER_API_VER,
            iam_apikey=TONEANALYZER_API_KEY,
            url=TONEANALYZER_API_URL
        )

    def get_tone_from_text(self, text):
        """
        :sample return:
        {
        "document_tone": {
            "tones": [
            {
                "score": 0.880435,
                "tone_id": "joy",
                "tone_name": "Joy"
            }
            ]
        }
        }
        """

        emotionalState = {
            "anger": 0.0,
            "fear": 0.0,
            "joy": 0.0,
            "sadness": 0.0,
            "analytical": 0.0,
            "confident": 0.0,
            "tentative": 0.0
        }

        if text is None or len(text) == 0:
            return emotionalState

        tone_analysis = self.tone_analyzer.tone(
            {'text': text},
            'application/json'
        ).get_result()

        for tone in tone_analysis['document_tone']['tones']:
            emotionalState[tone['tone_id']] = tone['score']

        return emotionalState
