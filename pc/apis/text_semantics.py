import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, SemanticRolesOptions
from config import SEMANTICS_API_KEY, SEMANTICS_API_URL, SEMANTICS_API_VER

"""
        from apis.text_semantics import SemanticsAnalyzer
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
        response = self.semantics_analyzer.analyze(
            text='IBM has one of the largest workforces in the world',
            features=Features(semantic_roles=SemanticRolesOptions())).get_result()

        return (response['semantic_roles'] if 'semantic_roles' in response else [])

