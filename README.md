# shakespeare-and-company-online-readership

This repository provides data and implements the network analysis for
"The Afterlives of Shakespeare and Company in Online Social Readership."

### Matching Shakespeare and Company with Goodreads

This project contributes a matching between works
in the [Shakespeare and Company Project][] and works in Goodreads.
We were able to match and manually verify 4460
of the Shakespeare and Company book URIs to Goodreads book IDs.
We additionally consolidated Goodreads metadata for these matched works.
- `data/goodreads-book-id-to-sc-uri_full-matching.json`: a JSON dictionary mapping Goodreads book ID to SC book URI
- `data/matched-goodreads-metadata.json`: a JSON list containing a dictionary for each matched Goodreads book. Example metadata keys are the year of publication (`yearFirstPublished`) and number of reviews (`numReviews`).

[Shakespeare and Company]: https://shakespeareandco.princeton.edu/about/data/

### Code requirements

This code needs Python 3 along with `numpy` and `networkx`.
You can install the dependencies with:
```
pip3 install -r requirements.txt
```

It additionally requires Version 1.1 of the data from the
[Shakespare and Company Project](https://shakespeareandco.princeton.edu/about/data/).
Please download the following files and place them in the `data` directory:
- [`SCoData_books_v1.1_2021-01.json`](https://dataspace.princeton.edu/bitstream/88435/dsp016d570067j/3/SCoData_books_v1.1_2021-01.json): the Shakespeare and Company books dataset
- [`SCoData_members_v1.1_2021-01.json`](https://dataspace.princeton.edu/bitstream/88435/dsp01b5644v608/3/SCoData_members_v1.1_2021-01.json): the Shakespeare and Company members dataset
- [`SCoData_events_v1.1_2021-01.json`](https://dataspace.princeton.edu/bitstream/88435/dsp012n49t475g/3/SCoData_events_v1.1_2021-01.json): the Shakespeare and Company events dataset


### Other included data

In addition to data from the Shakespeare and Company Project,
this project uses a preprocessed subset of the Goodreads data in the
[UCSD Book Graph](https://sites.google.com/eng.ucsd.edu/ucsdbookgraph/home).

We further restrict our analysis to 1511 titles that are 1) in both the Shakespeare and Company dataset and the
[UCSD Book Graph](https://sites.google.com/eng.ucsd.edu/ucsdbookgraph/home)
and 2) have at least one neighboring vertex in the graphs we construct.
All remaining files contain only data for these 1511 titles.

Preprocessed data from the UCSD Book Graph:
- `data/book-uris-in-both-goodreads-and-sc.json`: the URIs of books in both SC and Goodreads
- `data/goodreads-book-id-to-text.json`: dict mapping Goodreads book ID to summary string
- `data/goodreads-user-to-books.json`: dict mapping Goodreads user ID to a list of books the user interacted with
- `data/goodreads-book-id-to-num-ratings.json`: dict mapping Goodreads book ID to number of user ratings on Goodreads

There are also files listing the descriptive text for each book:
- `data/sc-book-names.json`: descriptive text for books in Shakespeare and Company
- `data/goodreads-book-names.json`: descriptive text for books in Goodreads

And finally dictionaries linking books across SC and Goodreads:
- `data/goodreads-book-id-to-sc-uri.json`: dict mapping Goodreads book ID to SC book URI
- `data/goodreads-text-to-sc-text.json`: dict mapping Goodreads book summary string to SC book summary string


### Example of how to use the graphs

Graphs are constructed for datasets from Shakespeare and Company and Goodreads.
Vertices correspond to books. Edges correspond to people: two books have an edge
between them if the same user interacted with both books.

Check out `example.py` for some sample code that shows how to:
1. Print summary statistics for the graphs
2. Find out information about a specific book in the graph

As an example, it shows that 'Hippolytus' by Euripides has an edge to only five other books
in the Shakespeare and Company graph but is connected to 68 books (many of which are 'classics') in the Goodreads graph.



