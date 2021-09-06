from collections import defaultdict
import os
import random
import time

import pandas as pd


def main():

    base_path = '/Volumes/Passport-1/data/shakespeare-and-co'
    results_directory_path = base_path + '/query-results'
    combined_results_path  = base_path + '/goodreads_query_results.combined.csv'

    df_list = []
    for _file_name in os.listdir(results_directory_path):
        df_list.append(pd.read_csv(results_directory_path + '/' + _file_name))
    combined_df = pd.concat(df_list)

    combined_df.to_csv(combined_results_path)


if __name__ == '__main__':
    main()