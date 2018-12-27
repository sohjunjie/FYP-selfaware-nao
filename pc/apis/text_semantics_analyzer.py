import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, SemanticRolesOptions
from watson_developer_cloud.watson_service import WatsonApiException

from config import SEMANTICS_API_KEY, SEMANTICS_API_URL, SEMANTICS_API_VER

"""
demo: https://natural-language-understanding-demo.ng.bluemix.net/

        from apis.text_semantics_analyzer import SemanticsAnalyzer
        self.sa = SemanticsAnalyzer()
"""


class SemanticsAnalyzer():

    def __init__(self):
        self.semantics_analyzer = NaturalLanguageUnderstandingV1(
            version=SEMANTICS_API_VER,
            iam_apikey=SEMANTICS_API_KEY,
            url=SEMANTICS_API_URL
        )

    def get_semantics_from_text(self, text):
        """
        :sample return:
        [{'subject': {'text': 'IBM'},
          'sentence': 'IBM has one of the largest workforces in the world',
          'object': {'text': 'one of the largest workforces in the world'},
          'action': {'verb': {'text': 'have',
                              'tense': 'present'},
                     'text': 'has',
                     'normalized': 'have'}
        }]
        """
        if text is None:
            return []

        try:
            response = self.semantics_analyzer.analyze(
                text=text,
                features=Features(semantic_roles=SemanticRolesOptions())).get_result()
        except WatsonApiException as e:
            return []

        return (response['semantic_roles'] if 'semantic_roles' in response else [])
