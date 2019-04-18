from os import listdir
from os.path import isfile, join
import pandas as pd

from engine.datahandler import DataHandler

def main():
    filename = "output.csv"
    handler = DataHandler('./source/exp2')
    handler.save_stimuli_order(filename)
    handler.transform_exp_data(filename)
    handler.aggregate_exp_data(filename)

if __name__ == "__main__":
    main()
