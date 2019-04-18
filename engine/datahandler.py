from os import listdir, makedirs
from os.path import isfile, join
import pandas as pd

from engine.testsubject import TestSubject

class DataHandler:
    """
    source => csv
    csv => aggr
    """

    source_path = None
    result_path = None

    @property
    def source_files(self):
        filelist = [f for f in listdir(self.source_path) if isfile(join(self.source_path, f))]
        filelist.sort()
        return filelist

    @staticmethod
    def  check_directory(path):
        try:
            makedirs(path)
        except FileExistsError:
            pass

    @staticmethod
    def aggregation(data, column):
        """
        Aggrigates data by column provided

        params:
            data - Pandas DataFrame
            column - column name
        """
        aggregation={
             column:
            {
                "MIN": lambda x: x.min(skipna=True),
                "MAX":lambda x: x.max(skipna=True),
                "MEDIAN":lambda x: x.median(skipna=True),
                "MEAN":lambda x:x.mean(skipna=True)
            }
        }
        return data.groupby(['stimulus', 'event']).agg(aggregation).reset_index()

    @staticmethod
    def calc_data(data):
        data_count = data['Number'].apply(pd.to_numeric).max()
        data_duration = data['Duration'].unique()
        data_duration = pd.to_numeric(data_duration, downcast='integer')
        data_duration_avg = data_duration.mean()
        data_duration_sum = data_duration.sum()
        return {
            'count':data_count,
            'duration_avg':data_duration_avg,
            'duration_sum':data_duration_sum
        }

    def process_testsubject(self, test_subject ):
        events = test_subject.events
        stimuli = test_subject.stimuli
        result = list()
        init_dict = {
            'subject': test_subject.subject
        }
        for stimulus in stimuli:
            init_dict['stimulus'] = stimulus
            for event in events:
                init_dict['event'] = event
                data = test_subject.get_data(stimulus, event)
                calculations = self.calc_data(data)
                calculations.update(init_dict)
                result.append(calculations)
        print(f'Subject {test_subject.subject} done!')
        return result


    def write_csv(self, filename, data):
        path = join(self.result_path, filename)
        data_frame = pd.DataFrame(data)
        text_file = open(path, "w")
        text_file.write(data_frame.to_csv(index=False))
        text_file.close()
        print(f"{filename} was written.")

    def read_csv(self, filename):
        print(f"Read {filename}")
        path = join(self.result_path, filename)
        return pd.read_csv(path)


    def transform_exp_data(self, filename):
        all_data = list()
        for source_file in self.source_files:
            test_subject = TestSubject(join(self.source_path, source_file))
            all_data += self.process_testsubject( test_subject )
        self.write_csv(filename, all_data)

    def save_stimuli_order(self, filename):
        all_data = list()
        for source_file in self.source_files:
            test_subject = TestSubject(join(self.source_path, source_file))
            all_data.append(test_subject.stimuli_order)
        self.write_csv(f"stimuli_order_{filename}", all_data)


    def aggregate_exp_data(self, filename):
        data = self.read_csv(filename)

        dur_sum = self.aggregation(data, 'duration_sum')
        self.write_csv('agg_dur_sum.csv', dur_sum)

        dur_avg = self.aggregation(data, 'duration_avg')
        self.write_csv('agg_dur_avg.csv', dur_avg)

        count = self.aggregation(data, 'count')
        self.write_csv('agg_count.csv', count)

    def __init__(self, source_path):
        self.source_path = source_path
        self.result_path = join(source_path, 'result')
        self.check_directory(self.result_path)
