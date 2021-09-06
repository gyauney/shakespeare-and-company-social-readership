from collections import defaultdict
import random
import time

import pandas as pd

import goodreads_api_client as gr


def get_result_dict(_book, _title, _author, _id, _result_num):

    _ratings_count = _book['ratings_count']
    if '#text' in _book['ratings_count']:
        _ratings_count = _book['ratings_count']['#text']

    _text_reviews_count = _book['text_reviews_count']
    if '#text' in _book['text_reviews_count']:
        _text_reviews_count = _book['text_reviews_count']['#text']

    _original_publication_year = _book['original_publication_year']
    if '#text' in _book['original_publication_year']:
        _original_publication_year = _book['original_publication_year']['#text']

    _average_rating = _book['average_rating']
    if '#text' in _book['average_rating']:
        _average_rating = _book['average_rating']['#text']

    return {'Result Number': _result_num,
            'Query Title': _title,
            'Query Author': _author,
            'Query ID': _id,
            'Result ID': _book['best_book']['id']['#text'],
            'Result Title': _book['best_book']['title'],
            'Result Author': _book['best_book']['author']['name'],
            'Ratings Count': _ratings_count,
            'Text Reviews Count': _text_reviews_count,
            'Original Publication Year': _original_publication_year,
            'Average Rating': _average_rating}



def main():

    base_path = '/Volumes/Passport-1/data/shakespeare-and-co'
    books_path  = base_path + '/SCoData_books_v1.1_2021-01.csv'
    events_path = base_path + '/SCoData_events_v1.1_2021-01.csv'
    # output_path = base_path + '/goodreads_query_results.csv'
    # output_path = base_path + '/goodreads_query_results'
    output_path = base_path + '/query-results'


    books_df = pd.read_csv(books_path) #.sample(10)

    titles = books_df['title'].tolist()
    authors = books_df['author'].tolist()
    ids = books_df['uri'].tolist()

    print(len(ids), len(list(set(ids))))

    client = gr.Client(developer_key='yfpOrUMd6wUM6NPCStscg')

    result_dicts = []
    i = 1

    for _title, _author, _id in zip(titles, authors, ids):

        if i > 400:

            _title = str(_title)
            _author = str(_author)
            if ',' in _author:
                _author = _author.split(',')[1].strip() + ' ' + _author.split(',')[0].strip()

            print('QUERY #' + str(i) + ': ' + _title + ' (' + _author + ')...')

            _results = client.search_book(q=_title + ' ' + _author)

            if _results['results']:

                _result_num = 0

                if type(_results['results']['work']) == list:
                    for _book in _results['results']['work']:
                        result_dicts.append(get_result_dict(_book, _title, _author, _id, _result_num))
                        _result_num += 1
                else:
                    result_dicts.append(get_result_dict(_results['results']['work'], _title, _author, _id, _result_num))

            else:
                result_dicts.append({'Result Number': None,
                                     'Query ID': _id,
                                     'Query Title': _title,
                                     'Query Author': _author,
                                     'Result ID': None,
                                     'Result Title': None,
                                     'Result Author': None,
                                     'Ratings Count': None,
                                     'Text Reviews Count': None,
                                     'Original Publication Year': None,
                                     'Average Rating': None})

            if i % 100 == 0:
                results_df = pd.DataFrame(result_dicts)
                results_df.to_csv(output_path + '/query_results.' + str(i) + '.csv')
                result_dicts = []

            time.sleep(1)

        i += 1

    results_df = pd.DataFrame(result_dicts)
    results_df.to_csv(output_path + '.' + str(i) + '.csv')


if __name__ == '__main__':
    main()