import matplotlib.pyplot as plt
import pandas as pd

STIMULI_EXP2 = {
    'piechart': range(2, 7),
    'horizontal': range(7, 12),
    'vertical': range(12, 17),
    'doughnut': range(17, 22),
}


def main():
    df = pd.read_csv('./source/exp2/result/answers_agg_data.csv', sep=',', header=0)
    print(df.columns)

    fig = plt.figure(1, figsize=(9, 6))
    # bp = df.boxplot(column='count_of_correct_answers', by='stimulus_type', showfliers=False)
    bp = df.boxplot(column='percent_of_correct_answers', by='stimulus_type', showfliers=False)
    print(bp)
    plt.show()


if __name__ == "__main__":
    main()