# shakespeare-and-company-and-goodreads-networks

This repository implements the network analysis for
"The Afterlives of Shakespeare and Company in Online Social Readership."

Graphs are constructed for datasets from Shakespeare and Company and Goodreads.
Vertices correspond to books. Edges correspond to people: two books have an edge
between them if the same user interacted with both books.

We also implement the community detection algorithm from
[An efficient and principled method for detecting communities in networks](https://arxiv.org/abs/1104.3590)
by Ball, Karrer, & Newman, 2011.

### Requirements

This code needs Python 3 along with `numpy` and `networkx`.
You can install the dependencies with:
```
pip3 install -r requirements.txt
```

### Included data

This paper uses data from the
[Shakespare and Company Project](https://shakespeareandco.princeton.edu/)
and a preprocessed subset of the Goodreads data in the
[UCSD Book Graph](https://sites.google.com/eng.ucsd.edu/ucsdbookgraph/home).


Several data files are included as of now (this will likely be removed in the final version):
- `data/SCoData_books_v1_2020-07.json`: the [Shakespeare and Company][] books dataset
- `data/SCoData_members_v1_2020-07.json`: the [Shakespeare and Company][] members dataset
- `data/SCoData_events_v1_2020-07.json`: the [Shakespeare and Company][] events dataset

Also included is preprocessed data from the UCSD Book Graph.
- `data/book-uris-in-both-goodreads-and-sc.json`: the URIs of books in both SC and Goodreads
- `data/goodreads-book-id-to-text.json`: dict mapping Goodreads book ID to summary string
- `data/goodreads-user-to-books.json`: dict mapping Goodreads user ID to a list of books the user interacted with

[Shakespeare and Company]: https://shakespeareandco.princeton.edu/about/data/

### Usage

The code has two command line arguments, one required and one optional:
- `--num_groups`: the number of communities to detect (required)
- `--verbose`: if passed, additional diagnostics will be printed during community detection (optional)

Running `graph.py` (the main file), will:
1. Run community detection on the simple
[Zachary's Karate Club](https://en.wikipedia.org/wiki/Zachary%27s_karate_club)
dataset (useful for understanding the data formats and outputs, will likely be removed in the final version).
2. Construct graphs for Shakespeare and Company and Goodreads.
3. Run the community detection algorithm on both graphs.

To run the code and detect, for example, 10 communities:
```
python3 graph.py --num_groups 10
```

Note: The community detection algorithm often takes hundreds or even thousands
of iterations to converge, so it may take a long time to run, but it should be fine on a laptop.