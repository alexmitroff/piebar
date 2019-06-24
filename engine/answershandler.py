from os.path import join
import re
from collections import OrderedDict
import pandas as pd

class AnswersHandler:
    """
    result structure:
    [
        [ subject, stimulus_type, count_of_correct_answers, stimulus_count, percent_of_correct_answers],
    ]
    """
    RESULT_INDEXES = ['subject', 'stimulus_type',
                      'count_of_correct_answers', 'stimulus_count', 'percent_of_correct_answers']
    ANSWERS = [1, 3, 2, 2, 3]

    EXP_2_STIMULI_BY_TYPE = {
        'piechart': range(2, 7),
        'horizontal': range(7, 12),
        'vertical': range(12, 17),
        'doughnut': range(17, 22),
    }

    EXP_2_TYPE_BY_STIMULI = {
        2: 'piechart',
        3: 'piechart',
        4: 'piechart',
        5: 'piechart',
        6: 'piechart',

        7: 'horizontal',
        8: 'horizontal',
        9: 'horizontal',
        10: 'horizontal',
        11: 'horizontal',

        12: 'vertical',
        13: 'vertical',
        14: 'vertical',
        15: 'vertical',
        16: 'vertical',

        17: 'doughnut',
        18: 'doughnut',
        19: 'doughnut',
        20: 'doughnut',
        21: 'doughnut'
    }

    def __init__(self, source_path):
        self.source = source_path
        self.result_path = join(source_path, 'result')
        self.result = None
        self.df = None
        self.subjects = None

    def read_file(self, filename):
        filepath = join(self.source, filename)
        df = pd.read_csv(filepath, sep='\t')
        self.df = df.rename(index=str, columns={"Unnamed: 4": "Type", "Unnamed: 5": "Is_correct"})

    def set_subjects(self):
        self.subjects = self.df['Subject'].unique()

    def get_correct_answer(self, stimulus):
        stimulus_type = self.get_stimulus_type(stimulus)
        answer_index = self.EXP_2_STIMULI_BY_TYPE[stimulus_type].index(stimulus)
        return self.ANSWERS[answer_index]

    def is_answer_correct(self, stimulus, answer):
        correct_answer = self.get_correct_answer(stimulus)
        return correct_answer == answer

    def get_stimulus_type(self, stimulus):
        return self.EXP_2_TYPE_BY_STIMULI[stimulus]

    def process_data(self):
        result = pd.DataFrame(columns=self.RESULT_INDEXES)

        for subject in self.subjects:
            subject_df = self.df[self.df['Subject'] == subject]
            subject_df = subject_df.sort_values('Source')
            for index, row in subject_df.iterrows():
                answer = int(row['Answer'][0])
                subject_df['Type'][index] = self.get_stimulus_type(row['Source'])
                subject_df['Is_correct'][index] = self.is_answer_correct(row['Source'], answer)

            subject_count_answers_df = subject_df.groupby('Type').count()
            subject_count_correct_answers_df = subject_df.groupby('Type').sum(level='Is_correct')

            for index, row in subject_count_answers_df.iterrows():
                subject_count_answers = row['Is_correct']
                subject_count_correct_answers = subject_count_correct_answers_df['Is_correct'][index]
                data = (
                    subject,
                    index,
                    subject_count_correct_answers,
                    subject_count_answers,
                    subject_count_correct_answers/subject_count_answers*100
                    )
                series = pd.Series(data, index=self.RESULT_INDEXES)
                result = result.append(series, ignore_index=True)

        self.result = result

    def write_result_as_csv(self, filename):
        path = join(self.result_path, filename)
        text_file = open(path, "w")
        text_file.write(self.result.to_csv(index=False))
        text_file.close()
        print(f"{filename} was written.")
