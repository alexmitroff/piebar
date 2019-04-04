import pandas as pd
import re

class TestSubject:
    """
    TestSubject{
        subject: username,
        stimuli:{
            stimulus_name:{
                Fixation: dataframe,
                Saccades: dataframe,
            }
        }
    }
    """

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
            #'Blink': blink_headers,
            #'UserEvent': userevents_headers
            }

    subject = ""
    stimuli = {}
    source = None

    def read_file(self):
        f = open(self.source, 'r')
        list_of_series = {}
        stimulus = "NaN"

        for line in f:
            line = line.rstrip()
            line = re.split(r'\t+', line.rstrip('\t'))
            id = line[0].split(' ')[0]

            if id == 'Subject:':
                self.subject = line[1]

            if id == 'UserEvent' and line[-1][-3:] in ['jpg', 'png']:
                stimulus = line[-1].split(' ')[-1]

            if stimulus is not "NaN" and stimulus not in self.stimuli:
                self.stimuli[stimulus] = {}

            if id in self.headers.keys():
                if self.stimuli[stimulus].get(id) is not None:
                    self.stimuli[stimulus][id].append(line)
                else:
                    self.stimuli[stimulus][id] = []


    def get_events(self):
        return list(self.headers.keys())

    def get_stimuli(self):
        return list(self.stimuli.keys())

    def get_data(self, stimulus, key):
        return pd.DataFrame(self.stimuli[stimulus].get(key), columns=self.headers.get(key))


    def __init__(self, source_file):
        self.source = source_file
        self.read_file()
