from os import listdir
from os.path import isfile, join
import pandas as pd

from engine.core import TestSubject

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

def process_testsubject( test_subject ):
    events = test_subject.get_events()
    stimuli = test_subject.get_stimuli()
    result = []
    init_dict = {
        'subject': test_subject.subject
    }
    for stimulus in stimuli:
        init_dict['stimulus'] = stimulus
        for event in events:
            init_dict['event'] = event
            data = test_subject.get_data(stimulus, event)
            calculations = calc_data(data)
            calculations.update(init_dict)
            result.append(calculations)
    print(f'Subject {test_subject.subject} done!')
    return result

def write_csv(filename, data):
    data_frame = pd.DataFrame(data)
    text_file = open(filename, "w")
    text_file.write(data_frame.to_csv(index=False))
    text_file.close()

def read_csv(filename):
    return pd.read_csv(filename)

def transform_exp_data(filename):
    mypath = "./source/exp1"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    #test_subject = TestSubject(join(mypath, onlyfiles[0]))
    #all_data = process_testsubject( test_subject )
    all_data = []
    for test_file in onlyfiles:
        test_subject = TestSubject(join(mypath, test_file))
        all_data += process_testsubject( test_subject )
    write_csv(filename, all_data)

def aggregation(data, column):
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

def main():
    filename = "Output.csv"
    #transform_exp_data(filename)

    data = read_csv(filename)

    dur_sum = aggregation(data, 'duration_sum')
    write_csv('dur_sum.csv', dur_sum)
    dur_avg = aggregation(data, 'duration_avg')
    write_csv('dur_avg.csv', dur_avg)
    count = aggregation(data, 'count')
    write_csv('count.csv', count)


if __name__ == "__main__":
    main()

"""
att = Attempt('test.txt')
fixations_count = att.fixations['Number'].apply(pd.to_numeric).max()
fixations_duration = att.fixations['Duration'].unique()
fixations_duration = pd.to_numeric(fixations_duration, downcast='integer')
fixations_duration_avg = fixations_duration.mean()
fixations_duration_sum = fixations_duration.sum()
print(fixations_duration_sum)
"""
