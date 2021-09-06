from graph import *
import numpy as np
import networkx as nx
import json
import csv
from collections import defaultdict, OrderedDict
import itertools
import operator
import math

from community_detection import get_communities

import argparse

# parse the command-line arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_groups', required=True, type=int)
    parser.add_argument('--verbose', action='store_true', default=False)
    return parser.parse_args()

def main():
    args = parse_args()

    # Test the community detection algorithm
    # with the simple "Zachary's Karate Club" dataset.
    # The vertices get split into two clear groups,
    # which you can see in the resulting text file 'karate_community-percents.txt'.
    G = nx.karate_club_graph()
    A = nx.to_numpy_array(G)
    vertices_in_order, edge_to_weight, vertex_to_neighbors, n = convert_adjacency_matrix_to_list(A)
    C = get_communities(edge_to_weight, vertex_to_neighbors, n, 2, 5, False)
    export_to_gephi(edge_to_weight, vertices_in_order, 'karate', C)
    save_vertices_by_group_percents(vertex_to_neighbors, C, 2, vertices_in_order, 'karate')

    # load the full shakespeare and company dataset
    books, members, events = load_shakespeare_and_company_data('data')
    book_uri_to_text = map_book_uris_to_text(books)
    
    # load the books that are present in both Shakespeare and Company and the UCSD Goodreads book graph
    # these were gotten in a separate preprocessing step
    with open('data/book-uris-in-both-goodreads-and-sc.json', 'r') as f:
        overlap_book_uris = json.load(f)
    # load a dict that maps from Goodreads book id to summary string
    # this was also constructed in a separate preprocessing step
    with open('data/goodreads-book-id-to-text.json', 'r') as f:
        goodreads_book_id_to_text = json.load(f)

    # get the data in the format we need to construct graphs
    # the lists of books have been pruned to only include:
    #    1) books that are common to both datasets
    #    2) books that will have at least one edge in the graphs
    #       n.b SC and Goodreads contain a different number of connected books,
    #           so the graphs have different numbers of vertices
    # these are dicts from person to books they interacted with
    sc_borrower_to_books = internal_get_sc_borrower_to_books(books, events, overlap_book_uris)
    with open('data/goodreads-user-to-books.json', 'r') as f:
        goodreads_user_to_books = json.load(f)

    # Shakespeare and Company: create a graph and run the community detection algorithm
    dataset = 'shakespeare-and-company_{}-groups'.format(args.num_groups)
    books_in_vertex_order, book_to_vertex_index, edge_to_weight, vertex_to_neighbors, n = create_books_graph(sc_borrower_to_books)
    print('Shakespeare and Company, # of vertices: {:,}'.format(n))
    print('Shakespeare and Company, # of unique edges: {:,}'.format(int(len(edge_to_weight)/2)))
    C = get_communities(edge_to_weight, vertex_to_neighbors, n, args.num_groups, 1, args.verbose)
    # save the results in html and gephi format
    save_html_with_community_summaries(n, edge_to_weight, vertex_to_neighbors, C, args.num_groups, books_in_vertex_order, dataset, book_uri_to_text)
    export_to_gephi(edge_to_weight, books_in_vertex_order, dataset, C)

    # Goodreads: create a graph and run the community detection algorithm
    dataset = 'goodreads_{}-groups'.format(args.num_groups)
    books_in_vertex_order, book_to_vertex_index, edge_to_weight, vertex_to_neighbors, n = create_books_graph(goodreads_user_to_books)
    print('Goodreads, # of vertices: {:,}'.format(n))
    print('Goodreads, # of unique edges: {:,}'.format(int(len(edge_to_weight)/2)))
    C = get_communities(edge_to_weight, vertex_to_neighbors, n, args.num_groups, 1, args.verbose)
    # save the results in html and gephi format
    save_html_with_community_summaries(n, edge_to_weight, vertex_to_neighbors, C, args.num_groups, books_in_vertex_order, dataset, goodreads_book_id_to_text)
    export_to_gephi(edge_to_weight, books_in_vertex_order, dataset, C)
    
if __name__ == '__main__':
    main()