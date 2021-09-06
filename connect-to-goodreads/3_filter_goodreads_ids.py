from collections import defaultdict
import random
import time

import pandas as pd

from Levenshtein import distance as levenshtein_distance


def get_score(row, query_title, query_author):
    return levenshtein_distance(query_title, r['Result Title']) + levenshtein_distance(query_author, r['Result Author'])


def get_best_match(df, query_title, query_author, query_id):

    # df['Score'] = df.apply(lambda row: get_score(row, query_title, query_author), axis=1)
    # df = df.sort_values('Score')

    df = df.sort_values('Ratings Count', ascending=False)

    return df.iloc[[0]]



def main():

    base_path = '/Volumes/Passport-1/data/shakespeare-and-co'
    books_path            = base_path + '/SCoData_books_v1_2020-07.csv'
    events_path           = base_path + '/SCoData_events_v1_2020-07.csv'
    results_path          = base_path + '/goodreads_query_results.combined.csv'
    filtered_results_path = base_path + '/goodreads_query_results_filtered.csv'

    print('Reading data...')

    books_df = pd.read_csv(books_path) #.sample(10)
    results_df = pd.read_csv(results_path)

    titles = books_df['title'].tolist()
    authors = books_df['author'].tolist()
    ids = books_df['uri'].tolist()

    print(len(titles), len(authors), len(ids))
    print(len(list(set(titles))), len(list(set(authors))), len(list(set(ids))))
    print(len(results_df['Query ID'].unique()))

    print('Filtering...')

    
    filtered_results_list = []

    for _title, _author, _id in zip(titles, authors, ids):

        _df = results_df[results_df['Query ID'] == _id]

        if len(_df.index) > 1:
            _best_match = get_best_match(_df, _title, _author, _id)
            filtered_results_list.append(_best_match)
        else:
            filtered_results_list.append(_df)

    print('Saving results...')

    filtered_results_df = pd.concat(filtered_results_list)
    filtered_results_df.to_csv(filtered_results_path)


if __name__ == '__main__':
    main()