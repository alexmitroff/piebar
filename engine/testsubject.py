import re
from collections import OrderedDict

import pandas as pd


class TestSubject:
    """
    TestSubject{
        subject: username,
        data:{
            stimulus_name:{
                Fixation: dataframe,
                Saccades: dataframe,
            }
        }
    }
    """
    EXP_2_STIMULI_BY_TYPE = {
        'piechart': range(2, 7),
        'horizontal': range(7, 12),
        'vertical': range(12, 17),
        'doughnut': range(17, 22),
    }

    userevents_headers = ['Event Type', 'Trial', 'Number', 'Start', 'Description']
    blink_headers = userevents_headers[:4] + ['End', 'Duration']
    fixation_headers = blink_headers + ['Location X', 'Location Y', 'Dispersion X',
                'Dispersion Y', 'Plane', 'Avg. Pupil Size X', 'Avg. Pupil Size Y']
    saccade_headers = blink_headers + ['Start Loc.X', 'Start Loc.Y', 'End Loc.X',
                'End Loc.Y', 'Amplitude', 'Peak Speed', 'Peak Speed At',
                'Average Speed', 'Peak Accel.', 'Peak Decel.', 'Average Accel.']

    headers = {
            'Fixation': fixation_headers,
            'Saccade': saccade_headers,
            # 'Blink': blink_headers,
            # 'UserEvent': userevents_headers
            }

    def __init__(self, source_file):
        self.source = source_file
        self.data = OrderedDict()
        self.subject = None
        self.stimuli_duration = None
        self.read_file()

    def set_stimuli_type(self):
        type_dicts = {}
        for chart_type, stimuli_numbers in self.EXP_2_STIMULI_BY_TYPE.items():
            file_name = 'experiment-{}.jpg'
            type_dict = { f'experiment-{number:02d}.jpg':chart_type for number in stimuli_numbers }
            type_dicts.update(type_dict)
        self.stimuli_types = type_dicts

    def read_file(self):
        f = open(self.source, 'r')
        stimulus = "NaN"
        self.stimuli_duration = {}

        for line in f:
            line = line.rstrip()
            line = re.split(r'\t+', line.rstrip('\t'))
            line_start = line[0].split(' ')[0]

            if line_start == 'Subject:':
                self.subject = line[1]

            if line_start == 'UserEvent' and line[-1][-3:] in ['jpg', 'png']:
                stimulus = line[-1].split(' ')[-1]

            if stimulus is not "NaN":
                if stimulus not in self.data:
                    self.data[stimulus] = {}
                if stimulus not in self.stimuli_duration:
                    self.stimuli_duration[stimulus] = {}

            if line_start in self.headers.keys():
                if len(line) == len(self.fixation_headers) or len(line) == len(self.saccade_headers):
                    if 'time_start' not in self.stimuli_duration[stimulus]:
                        self.stimuli_duration[stimulus]['time_start'] = int(line[3])
                    self.stimuli_duration[stimulus]['time_end'] = int(line[4])
                if self.data[stimulus].get(line_start) is not None:
                    self.data[stimulus][line_start].append(line)
                else:
                    self.data[stimulus][line_start] = []

    @property
    def events(self):
        return list(self.headers.keys())

    @property
    def stimuli(self):
        return list(self.data.keys())

    def get_stimulus_type(self, stimulus):
        if stimulus in self.stimuli_types:
            return self.stimuli_types[stimulus]
        return "additional"

    @property
    def stimuli_order(self):
        return [[self.subject, stimulus] for stimulus in self.stimuli]

    def get_data(self, stimulus, key):
        return pd.DataFrame(self.data[stimulus].get(key), columns=self.headers.get(key))

    def get_stimuli_durations(self):
        durations = {}
        for key, time_stamps in self.stimuli_duration.items():
            duration = time_stamps['time_end'] - time_stamps['time_start']
            durations[key] = duration
        return durations

    def get_stimuli_durations_as_list(self, subject, stumuli_duration):
        durations = []
        for key, time_stamps in stumuli_duration.items():
            if 'time_end' in time_stamps:
                duration = time_stamps['time_end'] - time_stamps['time_start']
                durations.append((subject, key, self.get_stimulus_type(key), duration))
        return durations

