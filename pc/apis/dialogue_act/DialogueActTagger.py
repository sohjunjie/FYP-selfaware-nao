import os
import pickle
from DialogueActTrain import DialogueActTrain as DA

"""
[usage]
from apis.dialogue_act.DialogueActTagger import DialogueActTagger
da = DialogueActTagger('apis\dialogue_act\model1')
da.dialogue_act_tag('tell me about yourself')
"""

class DialogueActTagger:
    def __init__(self, model_folder):
        self.acceptance_treshold = 0.5
        try:
            dimension_file_task = open(os.path.join(model_folder, "dimension_model_TASK"), "rb")
            self.dimension_model_task = pickle.load(dimension_file_task)
            dimension_file_som = open(os.path.join(model_folder, "dimension_model_SOM"), "rb")
            self.dimension_model_som = pickle.load(dimension_file_som)
            dimension_file_fb = open(os.path.join(model_folder, "dimension_model_FB"), "rb")
            self.dimension_model_fb = pickle.load(dimension_file_fb)
            task_file = open(os.path.join(model_folder, "task_model"), "rb")
            self.task_model = pickle.load(task_file)
            som_file = open(os.path.join(model_folder, "som_model"), "rb")
            self.som_model = pickle.load(som_file)
            # fb_file = open(os.path.join(model_folder, "fb_model"))
            # self.fb_model = pickle.load(fb_file)
        except OSError:
            print("The model folder does not contain the required models to run the DA tagger")
            print("Please run the train_all() method of the DialogueActTrain class to obtain the required models")
            exit(1)

    def dialogue_act_tag(self, sentence, prev_da=None):

        prev = True
        if prev_da is None:
            prev = False

        da = []

        if sentence[:8] == 'have we ':
            return [{'dimension': 'Task', 'communicative_function': 'PropQ'}]
        if sentence[:7] == 'have i ':
            return [{'dimension': 'Task', 'communicative_function': 'PropQ'}]
        if sentence[:12] == 'good evening':
            return [{'dimension': 'SocialObligationManagement', 'communicative_function': 'Salutation'}]
        if sentence[:14] == 'good afternoon':
            return [{'dimension': 'SocialObligationManagement', 'communicative_function': 'Salutation'}]
        if sentence[:5] == 'hello':
            return [{'dimension': 'SocialObligationManagement', 'communicative_function': 'Salutation'}]
        if sentence[:9] == 'hey hello':
            return [{'dimension': 'SocialObligationManagement', 'communicative_function': 'Salutation'}]

        utt = [sentence, prev_da]
        task_dim = self.dimension_model_task.predict_proba(DA.build_features([utt], prev=prev)[0])[0][1]
        som_dim = self.dimension_model_som.predict_proba(DA.build_features([utt], prev=prev)[0])[0][1]
        fb_dim = self.dimension_model_fb.predict_proba((DA.build_features([utt], prev=prev)[0]))[0][0]
        if task_dim > self.acceptance_treshold:
            da.append(
                {'dimension': "Task",
                 'communicative_function': self.task_model.predict(DA.build_features([utt], prev=prev)[0])[0]})
        if som_dim > self.acceptance_treshold:
            da.append({'dimension': "SocialObligationManagement",
                       'communicative_function': self.som_model.predict(DA.build_features([utt], prev=prev)[0])[0]})
        elif fb_dim > self.acceptance_treshold:
            da.append({'dimension': "Feedback", 'communicative_function': "Feedback"})
        return da

    def tag_task(self, sentence, prev_da=None):
        utt = [sentence, prev_da]
        return self.task_model.predict(DA.build_features([utt])[0])[0]

    def tag_som(self, sentence, prev_da=None):
        utt = [sentence, prev_da]
        return self.som_model.predict(DA.build_features([utt])[0])[0]
