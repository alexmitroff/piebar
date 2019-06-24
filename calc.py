from engine.datahandler import DataHandler


def main():
    print('Calc starts')
    filename = "output.csv"
    handler = DataHandler('./source/exp2')
    handler.save_stimuli_duration(filename)
    # handler.save_stimuli_order(filename)
    # handler.transform_exp_data(filename)
    # handler.aggregate_exp_data(filename)
    # handler.calc_pvalue('agg_count.csv')
    print('Calc done')


if __name__ == "__main__":
    main()
