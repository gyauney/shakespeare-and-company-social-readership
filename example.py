from graph import get_goodreads_graph, get_sc_graph
import operator
import json

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


# get the shakespeare and company graph!
sc_books_in_vertex_order, sc_book_to_vertex_index, sc_edge_to_weight, sc_vertex_to_neighbors, sc_n = get_sc_graph()
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
gr_books_in_vertex_order, gr_book_to_vertex_index, gr_edge_to_weight, gr_vertex_to_neighbors, gr_n = get_goodreads_graph()
# note: gr_books_in_vertex_order and gr_book_to_vertex_index
#      use full descriptive text for each book rather than just goodreads book id
print('\n---- Goodreads ----')
print_graph_summary(gr_books_in_vertex_order, gr_book_to_vertex_index, gr_edge_to_weight, gr_vertex_to_neighbors, gr_n)
# you can see all the book names in data/goodreads_book_names.json
get_neighbors_of_book('Euripides I: Alcestis / The Medea / The Heracleidae / Hippolytus by Euripides (428)',
                      gr_books_in_vertex_order, gr_book_to_vertex_index, gr_vertex_to_neighbors)


# ---------
# do your analysis with the Goodreads graph here!
# ---------





