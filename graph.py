import numpy as np
import networkx as nx
import json
import csv
from collections import defaultdict, OrderedDict
import itertools
import operator

from community_detection import get_communities

import argparse

# parse the command-line arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_groups', required=True, type=int)
    parser.add_argument('--verbose', action='store_true', default=False)
    return parser.parse_args()

'''
Load the three parts of the Shakespeare and Company dataset.

Input:
    folder: directory that contains the Shakespeare and Company data
Output:
    books: dict from book URI to book data
    members: dict from member URI to member data
    events: dict from event URI to event data
'''
def load_shakespeare_and_company_data(folder):
    with open('{}/SCoData_books_v1.1_2021-01.json'.format(folder), 'r') as f:
        books = {book['uri']: book for book in json.load(f)}
    with open('{}/SCoData_members_v1.1_2021-01.json'.format(folder), 'r') as f:
        members = {member['uri']: member for member in json.load(f)}
    with open('{}/SCoData_events_v1.1_2021-01.json'.format(folder), 'r') as f:
        events = json.load(f)
    return books, members, events

'''
Summarize each book's information into one string: [title] by [author] ([year])

Input:
    books: dict from book URI to book data for Shakespeare and Company
Output:
    book_to_text: dict from book URI to summary string
'''
def map_book_uris_to_text(books):
    book_to_text = {}
    for uri, value in books.items():
        author = ''
        year = ''
        if 'author' in books[uri]:
            author = ' by {}'.format(' & '.join(books[uri]['author']))
        if 'year' in books[uri]:
            year = ' ({})'.format(books[uri]['year'])
        book_to_text[uri] = '{}{}{}'.format(books[uri]['title'], author, year)
    return book_to_text

'''
Save a CSV file in Gephi format--Gephi is an extremely clunky but useful graph visualization program.

Input:
    edge_to_weight: dict from vertex index pair (u, v) to number of times book u and book v were interacted with by the same person
    books_in_vertex_order: list of book names in order
    dataset: dataset name for saving the file
    C: dict from edge to most likely community for that edge
'''
def export_to_gephi(edge_to_weight, books_in_vertex_order, dataset, C):
    print('Exporting {} to gephi!'.format(dataset))
    with open('./gephi-{}.gdf'.format(dataset), 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        # first write the vertices
        csvwriter.writerow(['nodedef>name VARCHAR', 'label VARCHAR', 'color VARCHAR'])
        for vertex_idx, book in enumerate(books_in_vertex_order):
            # use a muted blue as the default vertex color
            csvwriter.writerow([vertex_idx, book, '#8DA0CB'])
        # now write the edges, each with their most likely community
        # so that in Gephi we can give each community a different color
        csvwriter.writerow(['edgedef>node1 VARCHAR', 'node2 VARCHAR', 'group VARCHAR'])
        for (u, v) in edge_to_weight.keys():
            # each edge is in twice: (u,v) and (v,u), so only print the edge once, when u < v
            if v < u:
                continue
            csvwriter.writerow([u, v, C[(u,v)]])

'''
Find all the books in Shakespeare and Company that:
    1) are also in the Goodreads dataset
    2) were borrowed by a member
and map members to these books that they borrowed.

Input:
    books: dict from book URI to book data for Shakespeare and Company
    events: dict from event URI to event data for Shakespeare and Company
    keep_uris: set of book URIs that also occur in the Goodreads dataset. ignore the books not in this set
Output:
    borrower_to_books: dict from member URI to the URIs of the books that they borrowed
'''
def get_sc_borrower_to_books(books, events, keep_uris):
    borrower_to_books = defaultdict(set)
    for event in events:
        if event['event_type'] != 'Borrow':
            continue
        book_uri = event['item']['uri']
        # skip this book if it's not also in goodreads
        if book_uri not in keep_uris:
            continue
        for member_uri in event['member']['uris']:
            borrower_to_books[member_uri].add(book_uri)
    return borrower_to_books

'''
Construct an undirected graph.
Vertices: books
Edges: book u and book v are connected by an edge (u, v) if the same person interacted with both
       We are allowing multiple edges between books, one for each person in common
       Since the graph is undirected, both (u,v) and (v,u) are present.

Input:
    person_to_books: dict from member URI (or user ID) to all the books that person interacted with
                     assumes that this only contains books that lead to a connected graph
Output:
    books_in_vertex_order: list of book names in vertex order (the order is arbitrary but fixed)
    book_to_vertex_index: dict from book name to vertex index
    edge_to_weight: dict from vertex index pair (u, v) to number of times book u and book v were interacted with by the same person
    vertex_to_neighbors: dict from vertex index to a list of all neighboring vertex indices
    n: number of vertices in the graph
'''
def create_books_graph(person_to_books):
    # first create an edge between all pairs of books borrowed/reviewed by the same person
    # and get all the books that have at least one edge
    connected_vertices = set()
    E = []
    for person, books in person_to_books.items():
        for book_1, book_2 in itertools.combinations(books, 2):
            connected_vertices.add(book_1)
            connected_vertices.add(book_2)
            E.append((book_1, book_2))
    # in the constructed graph, each book is given an integer index
    # this is to make the community detection code closer to the paper's code
    books_in_vertex_order = list(connected_vertices)
    book_to_vertex_index = {v: i for i, v in enumerate(books_in_vertex_order)}
    n = len(books_in_vertex_order)
    edge_to_weight_unsorted = defaultdict(int)
    vertex_to_neighbors = defaultdict(set)
    for book_uri_1, book_uri_2 in E:
        l = book_to_vertex_index[book_uri_1]
        r = book_to_vertex_index[book_uri_2]
        edge_to_weight_unsorted[(l, r)] += 1
        edge_to_weight_unsorted[(r, l)] += 1
        vertex_to_neighbors[l].add(r)
        vertex_to_neighbors[r].add(l)
    # a consistent ordering is useful for the community detection code
    # sort lists of neighbors
    vertex_to_neighbors = {u: sorted(list(neighbors)) for u, neighbors in vertex_to_neighbors.items()}
    # sort edges
    edge_to_weight = OrderedDict()
    for u, neighbors in vertex_to_neighbors.items():
        for v in neighbors:
            edge_to_weight[(u, v)] = edge_to_weight_unsorted[(u, v)]
    return books_in_vertex_order, book_to_vertex_index, edge_to_weight, vertex_to_neighbors, n

'''
Convert a graph in adjacency matrix format to an adjacency list
Input:
    A: adjacency matrix as a numpy array of dimension (number of vertices) x (number of vertices) 
Output:
    vertices_in_order: list of vertex indices in vertex order (the order is arbitrary but fixed)
    edge_to_weight: dict from vertex index pair (u, v) to number of edges between u and v
    vertex_to_neighbors: dict from vertex index to a list of all neighboring vertex indices
    n: number of vertices in the graph
'''
def convert_adjacency_matrix_to_list(A):
    edge_to_weight = {}
    vertex_to_neighbors = defaultdict(list)
    vertices_in_order = []
    n = A.shape[0]
    for u in range(0, n):
        vertices_in_order.append(u)
        for v in range(0, n):
            if A[u, v] > 0:
                edge_to_weight[(u,v)] = A[u,v]
                vertex_to_neighbors[u].append(v)
    return vertices_in_order, edge_to_weight, vertex_to_neighbors, n

'''
Save an HTML file that summarizes all the communities.
For each community, list the vertices that have the highest percentage
of their incident edges in that community, with higher-degree vertices at the top.

Input:
    n: number of vertices
    edge_to_weight: dict from vertex index pair (u, v) to number of times book u and book v were interacted with by the same person
    vertex_to_neighbors: dict from vertex index to a list of all neighboring vertex indices
    C: dict from edge to most likely community for that edge
    K: number of groups
    books_in_vertex_order: list of book names in order
    dataset: dataset name for saving the file
    book_to_text: dict from book name to summary string
'''
def save_html_with_community_summaries(n, edge_to_weight, vertex_to_neighbors, C, K, books_in_vertex_order, dataset, book_to_text):
    # get the number of neighbors for each vertex
    degrees = {idx: sum([edge_to_weight[(idx, neighbor)] for neighbor in neighbors])
               for idx, neighbors in vertex_to_neighbors.items()}
    degrees_in_order = [degrees[i] for i in range(n)]
    
    html = ['<html> <link href="https://fonts.googleapis.com/css?family=Nunito:400,600,800" rel="stylesheet"> \
        <link href="https://fonts.googleapis.com/css?family=Nunito+Sans:400,600,800" rel="stylesheet"> \
        <style>body {font-family: "Nunito Sans"; font-size:12pt; padding:20px; display:block;} \
        p {font-family:sans-serif; padding-bottom:20px;} \
        img {margin: 10px 10px;} \
        .small-image {box-shadow: 8px 8px 4px grey; max-height: 100px; max-width: 200px;}\
        tr {padding-bottom:10px;} td {padding: 0px 10px;} \
        table {padding-top: 20px; display:inline-block;} \
        .header {font-size: 24pt; padding-bottom: 20px;} \
        .group-header {font-size: 18pt; padding-bottom: 5px; font-weight: 800;} \
        .bold {font-weight: 800;} \
        .gap {padding-bottom:20px} \
        ul {list-style-type: none;}\
        .small-list {float: left; width: 35%;} \
        .big-list {float: left; width: 55%; padding-right:5%;} \
        </style>']
    html.append('<body>')
    html.append('<div class="header">{}</div>'.format(dataset))
    html.append('<div>Vertices: {:,}</div>'.format(n))
    html.append('<div>Unique edges: {:,}</div>'.format(int(len(edge_to_weight)/2)))
    html.append('<div>Edges with multiplicity: {:,}</div>'.format(int(sum(list(edge_to_weight.values()))/2)))

    # first get the percentage of each node's edges in each group
    # store in an n * K (nodes by groups) matrix
    vertices_by_groups = np.zeros((n, K))
    for idx in range(n):
        # look at edge colors for this node, only where there is an edge
        edge_groups = np.array([C[(idx, neighbor)] for neighbor in vertex_to_neighbors[idx]])
        for z in range(K):
            vertices_by_groups[idx, z] = len(edge_groups[edge_groups==z])/len(edge_groups) 
    # now print highest-degree nodes in each community
    # sort by percent of edges in group then by degree
    for z in range(K):
        names = []
        summaries = []
        for percent, idx, uri, d in sorted(zip(vertices_by_groups[:, z], range(n), books_in_vertex_order, degrees_in_order),
                                            key=operator.itemgetter(0, 3),
                                            reverse=True)[:100]:
            if percent == 0:
                break
            name = book_to_text[uri]
            names.append(name)
            summaries.append('{} ({:.0f}% of {} edges)'.format(name, percent*100, d))
        html.append('<div class="gap"></div>')
        html.append('<div class="group-header">Group {}</div>'.format(z))
        html.append('<div>')
        names = '\n'.join(['<li>{}</li>'.format(name) for name in names])
        html.append('<div class="big-list">{}\n</div>'.format(names))
        html.append('</div>')
        html.append('<div style="clear:both;"></div>')
        html.append('<div style="float:none;"></div>')
    html.append('</body></html>')
    with open('{}.html'.format(dataset), 'w') as f:
        f.write('\n'.join(html))

'''
Save a simple .txt file that summarizes all the communities.
For each vertex, write the percentage of incident edges that belong to each community.
For use with karate club dataset.

Input:
    vertex_to_neighbors: dict from vertex index to a list of all neighboring vertex indices
    C: dict from edge to most likely community for that edge
    K: number of groups
    vertices_in_order: list of vertex names in order
    dataset: dataset name for saving the file
'''
def save_vertices_by_group_percents(vertex_to_neighbors, C, K, vertices_in_order, dataset):
    n = len(vertices_in_order)
    # first get the percentage of each node's edges in each group
    # store in an n * K (nodes by groups) matrix
    vertices_by_groups = np.zeros((n, K))
    for idx in range(n):
        # look at edge colors for this node, only where there is an edge
        edge_groups = np.array([C[(idx, neighbor)] for neighbor in vertex_to_neighbors[idx]])
        for z in range(K):
            vertices_by_groups[idx, z] = len(edge_groups[edge_groups==z])/len(edge_groups) 
    sorted_vertices_by_group_percents = vertices_by_groups[np.argsort(vertices_by_groups[:, 0])] * 100
    with open('{}_community-percents.txt'.format(dataset), 'w') as f:
        for idx in range(n):
            f.write('Vertex {}: {:.1f}, {:.1f}\n'.format(idx, sorted_vertices_by_group_percents[idx, 0],
                                                          sorted_vertices_by_group_percents[idx, 1]))

# for using the shakespeare and company graph
# note: indexes vertices by full descriptive text rather than book URI
def get_sc_graph():
    # load the full shakespeare and company dataset
    books, members, events = load_shakespeare_and_company_data('data')
    # limit to books also in goodreads
    with open('data/book-uris-in-both-goodreads-and-sc.json', 'r') as f:
        overlap_book_uris = json.load(f)
    # get a dict of person to books they borrowed
    sc_borrower_to_books = get_sc_borrower_to_books(books, events, overlap_book_uris)

    books_in_vertex_order, book_to_vertex_index, edge_to_weight, vertex_to_neighbors, n = create_books_graph(sc_borrower_to_books)

    # and now use more descriptive text for the books
    book_uri_to_text = map_book_uris_to_text(books)
    books_in_vertex_order = [book_uri_to_text[goodreads_id] for goodreads_id in books_in_vertex_order]
    book_to_vertex_index = {text: vertex_idx for vertex_idx, text in enumerate(books_in_vertex_order)}

    return books_in_vertex_order, book_to_vertex_index, edge_to_weight, vertex_to_neighbors, n 
    

# for using the goodreads graph
# note: indexes vertices by full descriptive text rather than goodreads id
def get_goodreads_graph():
    # get the preprocessed dict of person to books they reviewed
    with open('data/goodreads-user-to-books.json', 'r') as f:
        goodreads_user_to_books = json.load(f)
    books_in_vertex_order, book_to_vertex_index, edge_to_weight, vertex_to_neighbors, n = create_books_graph(goodreads_user_to_books)

    # and now use more descriptive text for the books
    with open('data/goodreads-book-id-to-text.json', 'r') as f:
        goodreads_book_id_to_text = json.load(f)
    books_in_vertex_order = [goodreads_book_id_to_text[goodreads_id] for goodreads_id in books_in_vertex_order]
    book_to_vertex_index = {text: vertex_idx for vertex_idx, text in enumerate(books_in_vertex_order)}

    return books_in_vertex_order, book_to_vertex_index, edge_to_weight, vertex_to_neighbors, n 


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
    sc_borrower_to_books = get_sc_borrower_to_books(books, events, overlap_book_uris)
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