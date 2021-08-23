from graph import get_goodreads_graph, get_sc_graph
import operator
import json
# move to the neighbor comparison file
from graph import get_goodreads_popularity_num_ratings, count_events_per_book_sc
import numpy as np
from scipy import stats


# print a few useful summary statistics for a graph
def print_graph_summary(books_in_vertex_order, book_to_vertex_index, edge_to_weight, vertex_to_neighbors, n):
    print('# of vertices: {:,}'.format(n))
    # all edges are included twice because these are undirected graphs
    print('# of unique edges: {:,}'.format(int(len(edge_to_weight)/2)))
    print('Total edge weights: {:,}'.format(int(sum(edge_to_weight.values())/2)))

    # list the five vertices with highest degree
    print('\nFive books with the most neighbors:')
    vertex_to_degree = {v: len(neighbors) for v, neighbors in vertex_to_neighbors.items()}
    vertex_to_degree_sorted = sorted(vertex_to_degree.items(), reverse=True, key=operator.itemgetter(1))
    for vertex_idx, degree in vertex_to_degree_sorted[:5]:
        vertex_book_name = books_in_vertex_order[vertex_idx]
        print('{} neighbors: {}'.format(degree, vertex_book_name))

# given a vertex's book name, print out the number of neighbors it has and some of their names
def get_neighbors_of_book(book_name, books_in_vertex_order, book_to_vertex_index, vertex_to_neighbors):
    vertex_idx = book_to_vertex_index[book_name]
    neighbors = vertex_to_neighbors[vertex_idx]
    print('\n{} vertices connected to {}.'.format(len(neighbors), book_name))
    # The book might have a lot of neighbors, so only print ten of them
    print('Names of up to ten of these neighbors (in the arbitrary but fixed vertex order):')
    for neighbor_idx in neighbors[:10]:
        print('Vertex {}: {}'.format(neighbor_idx, books_in_vertex_order[neighbor_idx]))

def get_vertex_adjacency_row(book_name, books_in_vertex_order, book_to_vertex_index, vertex_to_neighbors, edge_to_weight, n):
    adjacency = np.zeros(n)
    #print(adjacency.shape)
    vertex_idx = book_to_vertex_index[book_name]
    neighbors = vertex_to_neighbors[vertex_idx]
    for neighbor_idx in neighbors:
        #print('({}, {})'.format(book_name, books_in_vertex_order[neighbor_idx]), edge_to_weight[(vertex_idx, neighbor_idx)])
        adjacency[neighbor_idx] = edge_to_weight[(vertex_idx, neighbor_idx)]
    #print(adjacency)
    return adjacency

def get_vertex_adjacency_row_by_text(book_text, text_to_consistent_ordering, book_text_to_neighbor_texts, edge_text_to_weight, n):
    adjacency = np.zeros(n)
    #print(adjacency.shape)
    neighbor_texts = book_text_to_neighbor_texts[book_text]
    for neighbor_text in neighbor_texts:
        #print('({}, {})'.format(book_text, neighbor_text), edge_text_to_weight[(book_text, neighbor_text)])
        neighbor_idx = text_to_consistent_ordering[neighbor_text]
        adjacency[neighbor_idx] = edge_text_to_weight[(book_text, neighbor_text)]
    #print(adjacency)
    return adjacency

# get the shakespeare and company graph!
sc_books_in_vertex_order, sc_book_to_vertex_index, sc_edge_to_weight, sc_vertex_to_neighbors, sc_n, sc_book_uri_to_num_events, sc_book_uri_to_text = get_sc_graph()
# note: sc_books_in_vertex_order and sc_book_to_vertex_index
#      use full descriptive text for each book rather than just book URI
print('---- Shakespeare and Company ----')
print_graph_summary(sc_books_in_vertex_order, sc_book_to_vertex_index, sc_edge_to_weight, sc_vertex_to_neighbors, sc_n)
get_neighbors_of_book('Hippolytus by Euripides',
                      sc_books_in_vertex_order, sc_book_to_vertex_index, sc_vertex_to_neighbors)

# ---------
# do your analysis with the Shakespeare and Company graph here!
# ---------


# and now get the goodreads graph!
gr_books_in_vertex_order, gr_book_to_vertex_index, gr_edge_to_weight, gr_vertex_to_neighbors, gr_n, gr_book_id_to_num_ratings, gr_book_id_to_text = get_goodreads_graph()
# note: gr_books_in_vertex_order and gr_book_to_vertex_index
#      use full descriptive text for each book rather than just goodreads book id
print('\n---- Goodreads ----')
print_graph_summary(gr_books_in_vertex_order, gr_book_to_vertex_index, gr_edge_to_weight, gr_vertex_to_neighbors, gr_n)
# you can see all the book names in data/goodreads_book_names.json
get_neighbors_of_book('Hippolytus by Euripides, Richard Hamilton (2001)',
                      gr_books_in_vertex_order, gr_book_to_vertex_index, gr_vertex_to_neighbors)


# ---------
# do your analysis with the Goodreads graph here!
# ---------


# ---------
# analysis on both graphs!
# ---------

# TODO move to separate file

# TODO auxiliary function to construct consistent adjacency vectors

def compare_book_vectors_kl(sc_books_in_vertex_order, gr_books_in_vertex_order, sc_book_to_vertex_index, gr_book_to_vertex_index, sc_edge_to_weight, gr_edge_to_weight, sc_book_uri_to_num_events, gr_book_id_to_num_ratings, sc_n, gr_n, sc_book_uri_to_text, gr_book_id_to_text):
    print('Comparing neighbor distributions')
    
    # TODO update matchings with manually corrected mapping
    # first get books matched between goodreads and SC
    with open('data/goodreads-book-id-to-sc-uri.json', 'r') as f:
        goodreads_book_id_to_sc_uri = json.load(f)

    # TODO double check that initial vertex sets contain all connected vertices

    # filter both graphs to only overlapping books
    gr_text_to_book_id = {text: book_id for book_id, text in gr_book_id_to_text.items()}
    gr_text_in_both_graphs = set()
    sc_text_in_both_graphs = set()
    gr_text_to_consistent_ordering = {}
    sc_text_to_consistent_ordering = {}
    i = 0
    for gr_text in gr_books_in_vertex_order:
        gr_book_id = gr_text_to_book_id[gr_text]
        # ignore if not matched
        if gr_book_id not in goodreads_book_id_to_sc_uri:
            continue
        sc_uri = goodreads_book_id_to_sc_uri[gr_book_id]
        sc_text = sc_book_uri_to_text[sc_uri]
        # ignore if not also in SC graph
        if sc_text not in sc_book_to_vertex_index:
            continue
        gr_text_in_both_graphs.add(gr_text)
        sc_text_in_both_graphs.add(sc_text)
        gr_text_to_consistent_ordering[gr_text] = i
        sc_text_to_consistent_ordering[sc_text] = i
        i += 1
    assert(len(gr_text_in_both_graphs) == len(sc_text_in_both_graphs))


    # now remake books in vertex order and book to vertex index for both graphs
    combined_n = len(gr_text_in_both_graphs)
    gr_book_text_to_neighbor_texts = {}
    gr_edge_text_to_weight = {}
    for gr_text in gr_text_in_both_graphs:
        vertex_idx = gr_book_to_vertex_index[gr_text]
        neighbor_idxs = gr_vertex_to_neighbors[vertex_idx]
        neighbor_texts = [gr_books_in_vertex_order[neighbor_idx] for neighbor_idx in neighbor_idxs]
        # remove neighbors not in both graphs
        filtered_neighbor_texts = [n for n in neighbor_texts if n in gr_text_in_both_graphs]
        filtered_neighbor_idxs = [i for i, n in zip(neighbor_idxs, neighbor_texts) if n in gr_text_in_both_graphs]
        gr_book_text_to_neighbor_texts[gr_text] = filtered_neighbor_texts
        for neighbor_text, neighbor_idx in zip(filtered_neighbor_texts, filtered_neighbor_idxs):
            gr_edge_text_to_weight[(gr_text, neighbor_text)] = gr_edge_to_weight[(vertex_idx, neighbor_idx)]
    sc_book_text_to_neighbor_texts = {}
    sc_edge_text_to_weight = {}
    for sc_text in sc_text_in_both_graphs:
        vertex_idx = sc_book_to_vertex_index[sc_text]
        neighbor_idxs = sc_vertex_to_neighbors[vertex_idx]
        neighbor_texts = [sc_books_in_vertex_order[neighbor_idx] for neighbor_idx in neighbor_idxs]
        filtered_neighbor_texts = [n for n in neighbor_texts if n in sc_text_in_both_graphs]
        filtered_neighbor_idxs = [i for i, n in zip(neighbor_idxs, neighbor_texts) if n in sc_text_in_both_graphs]
        sc_book_text_to_neighbor_texts[sc_text] = filtered_neighbor_texts
        for neighbor_text, neighbor_idx in zip(filtered_neighbor_texts, filtered_neighbor_idxs):
            sc_edge_text_to_weight[(sc_text, neighbor_text)] = sc_edge_to_weight[(vertex_idx, neighbor_idx)]

    dists = []
    num_interactions_cutoff = 100
    for gr_book_id, sc_uri in goodreads_book_id_to_sc_uri.items():

        gr_text = gr_book_id_to_text[gr_book_id]
        sc_text = sc_book_uri_to_text[sc_uri]

        # skip books not connected in both graphs!
        if gr_text not in gr_text_in_both_graphs:
            continue

        # gr_adjacency_original = get_vertex_adjacency_row(gr_text, gr_books_in_vertex_order, gr_book_to_vertex_index, gr_vertex_to_neighbors, gr_edge_to_weight, gr_n)
        # sc_adjacency_original = get_vertex_adjacency_row(sc_text, sc_books_in_vertex_order, sc_book_to_vertex_index, sc_vertex_to_neighbors, sc_edge_to_weight, sc_n)

        gr_adjacency = get_vertex_adjacency_row_by_text(gr_text, gr_text_to_consistent_ordering, gr_book_text_to_neighbor_texts, gr_edge_text_to_weight, combined_n)
        sc_adjacency = get_vertex_adjacency_row_by_text(sc_text, sc_text_to_consistent_ordering, sc_book_text_to_neighbor_texts, sc_edge_text_to_weight, combined_n)

        if np.sum(sc_adjacency) < num_interactions_cutoff and np.sum(gr_adjacency) < num_interactions_cutoff:
            continue

        num_neighbors_gr = np.count_nonzero(gr_adjacency)
        num_neighbors_sc = np.count_nonzero(sc_adjacency)

        # uniform prior
        sc_adjacency += 0.1
        gr_adjacency += 0.1
        # normalize to probability distribution
        sc_adjacency = sc_adjacency / np.sum(sc_adjacency)
        gr_adjacency = gr_adjacency / np.sum(gr_adjacency)

        #kl = np.dot(sc_adjacency, np.log(sc_adjacency/gr_adjacency))
        kl = np.dot(gr_adjacency, np.log(gr_adjacency/sc_adjacency))
        dists.append((kl, sc_text, gr_text, num_neighbors_sc, num_neighbors_gr, sc_book_uri_to_num_events[sc_uri], gr_book_id_to_num_ratings[gr_book_id], stats.entropy(sc_adjacency), stats.entropy(gr_adjacency)))

    # get correlation with popularity
    kls = [d[0] for d in dists]
    sc_popularities = [d[5] for d in dists]
    goodreads_popularities = [int(d[6]) for d in dists]
    sc_num_neighbors = [d[3] for d in dists]
    gr_num_neighbors = [d[4] for d in dists]

    result = stats.spearmanr(sc_popularities, goodreads_popularities)
    #print('Spearman correlation between SC popularity and Goodreads popularity: {} ({:.8f} p-value)'.format(result.correlation, result.pvalue))
    print('{:.4f} (p={:.4f})'.format(result.correlation, result.pvalue))
    result = stats.spearmanr(kls, sc_popularities)
    #print('Spearman correlation between kl-divergence and SC popularity: {} ({:.8f} p-value)'.format(result.correlation, result.pvalue))
    print('{:.4f} (p={:.4f})'.format(result.correlation, result.pvalue))
    result = stats.spearmanr(kls, goodreads_popularities)
    #print('Spearman correlation between kl-divergence and Goodreads popularity: {} ({:.8f} p-value)'.format(result.correlation, result.pvalue))
    print('{:.4f} (p={:.4f})'.format(result.correlation, result.pvalue))
    result = stats.spearmanr(kls, sc_num_neighbors)
    #print('Spearman correlation between kl-divergence and SC number of neighbors: {} ({:.8f} p-value)'.format(result.correlation, result.pvalue))
    print('{:.4f} (p={:.4f})'.format(result.correlation, result.pvalue))
    result = stats.spearmanr(kls, gr_num_neighbors)
    #print('Spearman correlation between kl-divergence and Goodreads number of neighbors: {} ({:.8f} p-value)'.format(result.correlation, result.pvalue))
    print('{:.4f} (p={:.4f})'.format(result.correlation, result.pvalue))

    print('Highest KL-divergence:')
    for i, row in enumerate(sorted(dists, reverse=True)):
        if i >= 20:
            break
        print('{}\t{:.2f}\t{}\t{}\t{}\t{}\t{}'.format(i+1, row[0],  row[5], row[6], row[3], row[4], row[1]))
        #print('{}. {} ({} SC / {} GR)'.format(i+1, nameify(row[1]), row[3], row[4]))
    print('Lowest KL-divergence:')
    for i, row in enumerate(sorted(dists, reverse=False)):
        if i >= 20:
            break
        print('{}\t{:.2f}\t{}\t{}\t{}\t{}\t{}'.format(i+1, row[0],  row[5], row[6], row[3], row[4], row[1]))
        #print('{}. {} ({} SC / {} GR)'.format(i+1, nameify(row[1]), row[3], row[4]))
    print('Number of books with at least {} interactions: {}'.format(num_interactions_cutoff, len(dists)))

    # # plot kl vs. gr popularity
    # plot_distribution_differences(np.log(goodreads_popularities), kls, 'kl-divergence-vs-gr-popularity')
    # # plot kl vs. sc popularity
    # plot_distribution_differences(np.log(sc_popularities), kls, 'kl-divergence-vs-sc-popularity')

compare_book_vectors_kl(sc_books_in_vertex_order, gr_books_in_vertex_order, sc_book_to_vertex_index, gr_book_to_vertex_index, sc_edge_to_weight, gr_edge_to_weight, sc_book_uri_to_num_events, gr_book_id_to_num_ratings, sc_n, gr_n, sc_book_uri_to_text, gr_book_id_to_text)






