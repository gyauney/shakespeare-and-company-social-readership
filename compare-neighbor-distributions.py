from graph import get_goodreads_graph, get_sc_graph, \
                  get_goodreads_popularity_num_ratings, count_events_per_book_sc
import operator
import json
import numpy as np
from scipy import stats
import statistics

import math

# returns a row in the adjacency matrix for a graph
# requires that vertices have been given a consistent ordering across both graphs
def get_vertex_adjacency_row(book_name, books_in_vertex_order, book_to_vertex_index, vertex_to_neighbors, edge_to_weight, n, text_to_consistent_ordering):
    adjacency = np.zeros(n)
    vertex_idx = book_to_vertex_index[book_name]
    neighbors = vertex_to_neighbors[vertex_idx]
    for neighbor_idx in neighbors:
        neighbor_text = books_in_vertex_order[neighbor_idx]
        consistent_neighbor_idx = text_to_consistent_ordering[neighbor_text]
        adjacency[consistent_neighbor_idx] = edge_to_weight[(vertex_idx, neighbor_idx)]
    return adjacency
  
def compare_js_divergence():
    # get the shakespeare and company graph
    sc_books_in_vertex_order, sc_book_to_vertex_index, sc_edge_to_weight, sc_vertex_to_neighbors, sc_n, sc_book_uri_to_num_events, sc_book_uri_to_text, sc_book_uri_to_year, sc_book_uri_to_title, sc_book_uri_to_author = get_sc_graph()

    # and now get the goodreads graph
    gr_books_in_vertex_order, gr_book_to_vertex_index, gr_edge_to_weight, gr_vertex_to_neighbors, gr_n, gr_book_id_to_num_ratings, gr_book_id_to_text = get_goodreads_graph()

    print('Comparing neighbor distributions')
    
    with open('data/goodreads-book-id-to-sc-uri.json', 'r') as f:
        goodreads_book_id_to_sc_uri = json.load(f)

    # get a consistent ordering for the adjacency vectors of both graphs
    # in order to easily compare neighbor distributions
    gr_text_to_consistent_ordering = {}
    sc_text_to_consistent_ordering = {}
    for i, (gr_book_id, sc_uri) in enumerate(sorted(goodreads_book_id_to_sc_uri.items())):
        gr_text = gr_book_id_to_text[gr_book_id]
        sc_text = sc_book_uri_to_text[sc_uri]
        gr_text_to_consistent_ordering[gr_text] = i
        sc_text_to_consistent_ordering[sc_text] = i
    
    # get the texts in the arbitrary consistent order for showing the results at the end
    order_to_sc_text = {i: text for text, i in sc_text_to_consistent_ordering.items()}
    sc_text_in_order = [order_to_sc_text[i] for i in range(len(sc_text_to_consistent_ordering))]
    order_to_gr_text = {i: text for text, i in gr_text_to_consistent_ordering.items()}
    gr_text_in_order = [order_to_gr_text[i] for i in range(len(gr_text_to_consistent_ordering))]
    
    # first filter only to books in top quartile of popularity in both datasets
    sc_median_events = statistics.quantiles(sc_book_uri_to_num_events.values())[2]
    gr_median_ratings = statistics.quantiles(gr_book_id_to_num_ratings.values())[2]

    print('Top quartile for SC: {} borrows'.format(sc_median_events))
    print('Top quartile for GR: {} ratings'.format(gr_median_ratings))

    dists = []
    for gr_book_id, sc_uri in goodreads_book_id_to_sc_uri.items():

        # skip books not in top quartile of popularity in both datasets
        if sc_book_uri_to_num_events[sc_uri] < sc_median_events or gr_book_id_to_num_ratings[gr_book_id] < gr_median_ratings:
            continue 

        gr_text = gr_book_id_to_text[gr_book_id]
        sc_text = sc_book_uri_to_text[sc_uri]

        author = sc_book_uri_to_author[sc_uri]
        if ',' in author:
            author = '{} {}'.format(author.split(',')[1], author.split(',')[0])
        title = sc_book_uri_to_title[sc_uri]

        gr_adjacency = get_vertex_adjacency_row(gr_text, gr_books_in_vertex_order, gr_book_to_vertex_index, gr_vertex_to_neighbors, gr_edge_to_weight, len(gr_books_in_vertex_order), gr_text_to_consistent_ordering)
        sc_adjacency = get_vertex_adjacency_row(sc_text, sc_books_in_vertex_order, sc_book_to_vertex_index, sc_vertex_to_neighbors, sc_edge_to_weight, len(sc_books_in_vertex_order), sc_text_to_consistent_ordering)

        num_neighbors_gr = np.count_nonzero(gr_adjacency)
        num_neighbors_sc = np.count_nonzero(sc_adjacency)

        # uniform prior
        sc_adjacency += 0.01
        gr_adjacency += 0.01
        # normalize to probability distribution
        sc_adjacency = sc_adjacency / np.sum(sc_adjacency)
        gr_adjacency = gr_adjacency / np.sum(gr_adjacency)

        mean_adjacency = (sc_adjacency + gr_adjacency) / 2
        
        # look at two specific books
        if sc_uri in ['https://shakespeareandco.princeton.edu/books/faulkner-light-august/',
                      'https://shakespeareandco.princeton.edu/books/wilde-picture-dorian-grey/']:
            print(sc_uri)
            print('\tClosest neighbors in Shakespeare and Company:')
            for i, (num_same_borrowers, neighbor_text) in enumerate(sorted(zip(sc_adjacency, sc_text_in_order), reverse=True)[:10]):
                print('\t{}\t{}\t{}'.format(i, num_same_borrowers, neighbor_text))
            print('\tClosest neighbors in Goodreads:')
            for i, (num_same_borrowers, neighbor_text) in enumerate(sorted(zip(gr_adjacency, gr_text_in_order), reverse=True)[:10]):
                print('\t{}\t{}\t{}'.format(i, num_same_borrowers, neighbor_text))


        # calculate jensen-shannon divergence
        js = 0.5 * np.dot(sc_adjacency, np.log(sc_adjacency/mean_adjacency)) + 0.5 * np.dot(gr_adjacency, np.log(gr_adjacency/mean_adjacency))
        dists.append((js, sc_text, gr_text, num_neighbors_sc, num_neighbors_gr, sc_book_uri_to_num_events[sc_uri], gr_book_id_to_num_ratings[gr_book_id], stats.entropy(sc_adjacency), stats.entropy(gr_adjacency), title, author))

    # check correlations with popularities
    jsds = [d[0] for d in dists]
    sc_popularities = [d[5] for d in dists]
    goodreads_popularities = [int(d[6]) for d in dists]
    sc_num_neighbors = [d[3] for d in dists]
    gr_num_neighbors = [d[4] for d in dists]

    result = stats.spearmanr(jsds, sc_popularities)
    print('Correlation with SC popularity: {:.4f} (p={:.4f})'.format(result.correlation, result.pvalue))
    result = stats.spearmanr(jsds, goodreads_popularities)
    print('Correlation with GR popularity: {:.4f} (p={:.4f})'.format(result.correlation, result.pvalue))
    result = stats.spearmanr(jsds, sc_num_neighbors)
    print('Correlation with SC number of neighbors: {:.4f} (p={:.4f})'.format(result.correlation, result.pvalue))
    result = stats.spearmanr(jsds, gr_num_neighbors)
    print('Correlation with GR number of neighbors: {:.4f} (p={:.4f})'.format(result.correlation, result.pvalue))

    print('Highest Jensen-Shannon divergence:')
    for i, row in enumerate(sorted(dists, reverse=True)[:20]):
        print('{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(i+1, row[5], row[6], row[3], row[4], row[9], row[10]))
    print('Lowest Jensen-Shannon divergence:')
    for i, row in enumerate(sorted(dists, reverse=False)[:20]):
        print('{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(i+1, row[5], row[6], row[3], row[4], row[9], row[10]))
    print('Number of books in top quartile of popularity in both datasets: {}'.format(len(dists)))

if __name__ == '__main__':
    compare_js_divergence()




