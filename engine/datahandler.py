from os import listdir, makedirs
from os.path import isfile, join
import pandas as pd

from engine.testsubject import TestSubject
from scipy.stats import ttest_ind


class DataHandler:
    """
    source => csv
    csv => aggr
    """

    def __init__(self, source_path):
        self.source_path = source_path
        self.result_path = join(source_path, 'result')
        self.check_directory(self.result_path)
        self.plot_data = {}

    @property
    def source_files(self):
        filelist = [f for f in listdir(self.source_path) if isfile(join(self.source_path, f))]
        filelist.sort()
        return filelist

    @staticmethod
    def check_directory(path):
        try:
            makedirs(path)
        except FileExistsError:
            pass

    @staticmethod
    def aggregation(data, column, group_list=[]):
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
        return data.groupby(group_list).agg(aggregation).reset_index()

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

    def process_testsubject(self, test_subject):
        events = test_subject.events
        stimuli = test_subject.stimuli
        result = []
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

    def write_csv(self, filename, data, header=None):
        path = join(self.result_path, filename)
        data_frame = pd.DataFrame(data)
        text_file = open(path, "w")
        text_file.write(data_frame.to_csv(index=False, header=header))
        text_file.close()
        print(f"{filename} was written.")

    def read_csv(self, filename):
        print(f"Read {filename}")
        path = join(self.result_path, filename)
        return pd.read_csv(path)

    def transform_exp_data(self, filename):
        all_data = []
        for source_file in self.source_files:
            test_subject = TestSubject(join(self.source_path, source_file))
            all_data += self.process_testsubject(test_subject)
        self.write_csv(filename, all_data)

    def save_stimuli_order(self, filename):
        print('Save stimuli order')
        all_data = []
        for source_file in self.source_files:
            print(f'processing {source_file}')
            test_subject = TestSubject(join(self.source_path, source_file))
            all_data += test_subject.stimuli_order
        self.write_csv(f"stimuli_order_{filename}", all_data)

    def save_stimuli_duration(self, filename):
        print('Save stimuli duration')
        all_data = []
        for source_file in self.source_files:
            print(f'processing {source_file}')
            test_subject = TestSubject(join(self.source_path, source_file))
            test_subject.read_file()
            test_subject.set_stimuli_type()
            all_data += test_subject.get_stimuli_durations_as_list(test_subject.subject, test_subject.stimuli_duration)
        self.write_csv(f"stimuli_durations_{filename}", all_data, header=['subject', 'stimulus', 'stype', 'duration'])

    def aggregate_exp_data(self, filename):
        data = self.read_csv(filename)

        dur_sum = self.aggregation(data, 'duration_sum')
        self.write_csv('agg_dur_sum.csv', dur_sum, ['stimulus', 'event'])

        dur_avg = self.aggregation(data, 'duration_avg')
        self.write_csv('agg_dur_avg.csv', dur_avg, ['stimulus', 'event'])

        count = self.aggregation(data, 'count')
        self.write_csv('agg_count.csv', count, ['stimulus', 'event'])

    @staticmethod
    def cleanup_dataframe(dataframe):
        print('Cleanup Dataframe')
        dataframe = dataframe[dataframe.event != 'Saccade']
        # dataframe = dataframe[dataframe.event != 'Fixation']
        # dataframe = dataframe[dataframe.stimulus.astype(str).str.startswith('rc-')]
        # dataframe = dataframe[~dataframe.stimulus.astype(str).str.startswith('rc-experiment-01.jpg')]
        dataframe = dataframe[dataframe.stimulus.astype(str).str.startswith('exp')]
        dataframe = dataframe[~dataframe.stimulus.astype(str).str.startswith('experiment-01.jpg')]
        return dataframe

    @staticmethod
    def separate_dataframe_by_group(dataframe):
        print('Separate by group')
        print(dataframe)
        print('Shape: ', dataframe.shape)
        df_list = []

        step = 5
        for i in range(4):
            # df_list.append(list(dataframe[step*i:step+step*i]['duration_avg.3'].astype(float)))
            df_list.append(list(dataframe[step*i:step+step*i]['count.3'].astype(float)))
        return df_list

    def calc_pvalue(self, filename):
        data = self.read_csv(filename)
        data = self.cleanup_dataframe(data)
        data_groups = self.separate_dataframe_by_group(data)

        print('Groups: ', data_groups)

        i = 1
        for group in data_groups:
            j = i+1
            for last_group in data_groups[i:]:
                ttest = ttest_ind(group, last_group)
                print(f'{i} & {j}: ', ttest.pvalue)
                j += 1
            i += 1

    def process_testsubject_plot(self, test_subject):
        events = test_subject.events
        stimuli = test_subject.stimuli
        for stimulus in stimuli:
            if not stimulus.startswith('exp'):
                continue

            if stimulus not in self.plot_data:
                self.plot_data.update({
                    stimulus: {
                        'Fixation': [],
                        'Fixation_count': [],
                        'Saccade': [],
                        'Saccade_count': []
                    }
                })

            for event in events:
                if event not in self.plot_data[stimulus]:
                    continue

                data = test_subject.get_data(stimulus, event)
                data_duration = data['Duration']
                data_duration = pd.to_numeric(data_duration, downcast='integer')
                self.plot_data[stimulus][event] += list(data_duration)
                self.plot_data[stimulus][f'{event}_count'].append(len(data_duration))
            print(f'{stimulus} data added')

    def transform_data_for_plots(self):
        all_data = []
        for source_file in self.source_files:
            test_subject = TestSubject(join(self.source_path, source_file))
            self.process_testsubject_plot(test_subject)