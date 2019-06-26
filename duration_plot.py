import matplotlib.pyplot as plt
import pandas as pd

from engine.datahandler import DataHandler


def main():
    dataframe = pd.read_csv('./source/exp2/result/stimuli_durations_output.csv', sep=',', header=0)
    dataframe = dataframe[dataframe.stype.astype(str) != 'additional']
    aggr = DataHandler.aggregation(dataframe, 'duration', ['stype'])
    print(aggr)

    fig = plt.figure(1, figsize=(9, 6))
    # bp = df.boxplot(column='count_of_correct_answers', by='stimulus_type', showfliers=False)
    bp = dataframe.boxplot(column='duration', by='stimulus', showfliers=False)
    # print(bp)
    plt.show()


if __name__ == "__main__":
    main()