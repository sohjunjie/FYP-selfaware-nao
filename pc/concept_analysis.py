import json, random, re

from apis import utils
from config import START_STATE
from config import GREETING_STATE
from config import FEEDFORWARD_STATE
from config import CONVERSATION_STATE
from config import CONVERSATION_EXCEPT_STATE
from config import CONVERSATION_ABOUTME_STATE
from config import CONVERSATION_MYACTIVITY_STATE
from config import CONVERSATION_GENERAL_STATE
from config import CONVERSATION_ABOUTHUMAN_STATE
from config import CONVERSATION_HUMANACTIVITY_STATE
from config import FEEDBACK_STATE
from config import CLOSING_STATE
from config import END_STATE

import concepts


class ConceptAnalyzer():
    def __init__(self, memory, dialogueManager):
        self.memory = memory
        self.dialogueManager = dialogueManager

    def build_bigram_speeches(self, state, semantics, dialogue_acts, context, temporals, robot_exp):
        prev_speech = None
        if 'prev_speech'  in context:
            prev_speech = context['prev_speech']
        cur_speech = {
            'speech': robot_exp['speech'],
            'speaker': robot_exp['subject'],
            'dialogue_acts': dialogue_acts,
            'semantics': semantics,
            'state': state,
            'temporals': temporals,
            'isfeedforward': False
        }
        return cur_speech, prev_speech

    def concept_to_response(self, state, semantics, dialogue_acts, context, temporals, robot_exp):

        # consider prev 2 speech to predict current robot response
        cur_speech, prev_speech = self.build_bigram_speeches(state,
                                                             semantics,
                                                             dialogue_acts,
                                                             context,
                                                             temporals,
                                                             robot_exp)
        def determine_response():

            if cur_speech['speech'] in concepts.COMMON_RESPONSE_MAPPINGS:
                return concepts.COMMON_RESPONSE_MAPPINGS[cur_speech['speech']]

            if not context['robot_greeted']:
                return self.handle_greeting_response(context, cur_speech)

            if cur_speech['state'] == GREETING_STATE:
                return self.handle_feedforward_response(context,
                                                        cur_speech,
                                                        robot_initiate=True)

            elif cur_speech['state'] == FEEDFORWARD_STATE:
                return self.handle_feedforward_response(context,
                                                        cur_speech,
                                                        robot_initiate=False)

            if len(cur_speech['semantics']) == 0:
                return 'sorry, can you rephrase your question'

            if cur_speech['speech'] == 'that is very interesting.':
                print(semantics)
                print(cur_speech['dialogue_acts'])

            semantic = max(cur_speech['semantics'], key=lambda x: utils.extract_relevant_semantic(x))
            # handle concuring to human response
            if any((x['dimension'] == 'Task' and
                    x['communicative_function'] == 'Statement') for x in cur_speech['dialogue_acts']):

                if semantic['subject']['text'] == 'we' and semantic['action']['normalized'] == 'have':
                    return '{subject} do {verb} {object}'.format(subject=semantic['subject']['text'],
                                                                 verb=semantic['action']['normalized'],
                                                                 object=semantic['object']['text'])

            # handle concuring to human response
            if any((x['dimension'] == 'Feedback' and
                    x['communicative_function'] == 'Feedback') for x in cur_speech['dialogue_acts']):

                if semantic['subject']['text'] == 'that' and semantic['action']['normalized'] == 'be':
                    return 'it {verb} {object}'.format(verb=semantic['action']['text'],
                                                       object=semantic['object']['text'])

            if cur_speech['state'] == CONVERSATION_ABOUTME_STATE:
                return self.handle_conversation_aboutme(context, cur_speech)

            if cur_speech['state'] == CONVERSATION_ABOUTHUMAN_STATE:
                return self.handle_conversation_abouthuman(context, cur_speech)

            if cur_speech['state'] == FEEDBACK_STATE:
                return self.handle_feedback_response(context, cur_speech)

            if (cur_speech['state'] == CLOSING_STATE) and (not context['robot_bid_farewell']):
                return self.handle_closing_response(context, cur_speech)

        context['prev_speech'], context['prev2_speech'] = cur_speech, prev_speech

        return determine_response()


    def handle_greeting_response(self, context, cur_speech):

        if cur_speech['state'] == START_STATE:
            return '' # random.choice(concepts.GREETING)

        if cur_speech['state'] == GREETING_STATE and cur_speech['speaker'] != 'me':
            return random.choice(concepts.GREETING)

    def handle_feedforward_response(self, context, cur_speech, robot_initiate):

        cur_speech['isfeedforward'] = True
        if robot_initiate:
            # robot initiate feedforward
            return random.choice(concepts.FEEDFORWARD)
        else:
            # robot reply human feedforward
            if any((x['dimension'] == 'Task' and
                    x['communicative_function'] == 'PropQ') for x in cur_speech['dialogue_acts']):
                semantic_act = cur_speech['semantics'][0]['action']
                semantic_sbj = cur_speech['semantics'][0]['subject']
                semantic_obj = cur_speech['semantics'][0]['object']

                # question is about robot meeting human
                if semantic_act['normalized'] in ["meet" or "see"] and \
                   semantic_act['verb']['tense'] == "past" and \
                   semantic_sbj['text'] == "i" and \
                   semantic_obj['text'] == "you":
                    if len(cur_speech['temporals']) == 0:
                        if self.memory.have_met_before(cur_speech['speaker']):
                            return "yes, we we have met before"
                        else:
                            return "no, i believe this is the first time we have met"

        # fall back response
        return "i think so too"

    def handle_conversation_aboutme(self, context, cur_speech):

        # current speaker is human
        if cur_speech['speaker'] != 'me':

            semantic_act = cur_speech['semantics'][0]['action']
            semantic_obj = cur_speech['semantics'][0]['object']
            semantic_sbj = cur_speech['semantics'][0]['subject']

            if any((x['dimension'] == 'Task' and
                    x['communicative_function'] == 'Directive') for x in cur_speech['dialogue_acts']):

                if semantic_act['normalized'] == "tell" and "about yourself" in semantic_obj['text']:
                    return random.choice(concepts.INTRO_OPEN)

            if any((x['dimension'] == 'Task' and
                    x['communicative_function'] == 'SetQ') for x in cur_speech['dialogue_acts']):

                if semantic_act['normalized'] == "do" and "companion robot" in semantic_obj['text']:
                    return "my duty is caring for someone who needs caring on a day-to-day basis"

                if semantic_act['normalized'] == "be" and semantic_sbj['text'] == "what":
                    queryProp = utils.strip_possessive(semantic_obj['text'])
                    propVal = self.memory.query_robot(queryProp)
                    if len(propVal) == 0:
                        return 'sorry, i do not know the answer to your question'
                    else:
                        return 'my {paramProp} is {paramVal}'.format(paramProp=queryProp,
                                                                     paramVal=propVal)

            if any((x['dimension'] == 'Task' and
                    x['communicative_function'] == 'PropQ') for x in cur_speech['dialogue_acts']):
                pass


    def handle_conversation_abouthuman(self, context, cur_speech):

        if cur_speech['speaker'] != 'me':

            semantic = max(cur_speech['semantics'], key=lambda x: utils.extract_relevant_semantic(x))
            semantic_act = semantic['action']
            semantic_obj = semantic['object']

            if any((x['dimension'] == 'Task' and
                    x['communicative_function'] == 'Commissive') for x in cur_speech['dialogue_acts']):
                return "okay"

            # robot comment on semantics with longest object length
            if any((x['dimension'] == 'Task' and
                    x['communicative_function'] == 'Statement') for x in cur_speech['dialogue_acts']):

                if semantic_act['normalized'] == 'be' and semantic_act['verb']['tense'] == 'present':
                    resp = random.choice(concepts.COMMENT_HUMAN)
                    return resp.format(param=semantic_obj['text'])

                if semantic_act['normalized'] == 'like' and semantic_act['verb']['tense'] == 'present':
                    self.dialogueManager.state = CONVERSATION_ABOUTME_STATE
                    return random.choice(concepts.INTRO_LIKES)

            if any((x['dimension'] == 'Task' and
                    x['communicative_function'] == 'Directive') for x in cur_speech['dialogue_acts']):

                if semantic_act['normalized'] == "tell":
                    queryProp = utils.strip_possessive(semantic_obj['text'])
                    propVal = self.memory.query_robot(queryProp)
                    print('prop: ', queryProp)
                    if len(propVal) == 0:
                        return 'sorry, i do not know the answer to your question'
                    else:
                        return 'your {paramProp} is {paramVal}'.format(paramProp=queryProp,
                                                                       paramVal=propVal)

    def handle_feedback_response(self, context, cur_speech):
        return "oh you have to go now?"

    def handle_closing_response(self, context, cur_speech):
        return random.choice(concepts.CLOSING)
