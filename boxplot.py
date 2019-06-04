from engine.datahandler import DataHandler
import matplotlib as mpl
import matplotlib.pyplot as plt

## SVG backend is used to create plot as a .svg file
mpl.use('SVG')

STIMULI_EXP2 = {
    'piechart': range(2, 7),
    'horizontal': range(7, 12),
    'vertical': range(12, 17),
    'doughnut': range(17, 22),
}


def main():
    field = 'Saccade_count'
    handler = DataHandler('./source/exp2')
    handler.transform_data_for_plots()

    # for stimulus, events in handler.plot_data.items():
    #     data_for_plot.append(events['Fixation_count'])

    labels = []
    data_for_plot = []

    for chart_name, numbers in STIMULI_EXP2.items():
        labels.append(chart_name)
        data = []
        for number in numbers:
            stimulis_name = f'experiment-{number:02d}.jpg'
            data += handler.plot_data[stimulis_name][field]
        data_for_plot.append(data)

    fig = plt.figure(1, figsize=(9, 6))
    ax = fig.add_subplot(111)
    bp = ax.boxplot(data_for_plot, showfliers=False)
    ax.set_xticklabels(labels)
    fig.savefig('exp2__saccade__count.svg', bbox_inches='tight')


if __name__ == "__main__":
    main()