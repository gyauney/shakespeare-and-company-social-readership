# shakespeare-and-company-online-readership

This repository provides data and code to accompany
"The Afterlives of Shakespeare and Company in Online Social Readership."

### Matching Shakespeare and Company with Goodreads

This project contributes a matching between works
in the [Shakespeare and Company Project][] and works in Goodreads.
We were able to match and manually verify 4460
of the Shakespeare and Company book URIs to Goodreads book IDs.
We additionally consolidated Goodreads metadata for these matched works.
- `data/goodreads-book-id-to-sc-uri_full-matching.json`: a JSON dictionary mapping Goodreads book ID to SC book URI
- `data/matched-goodreads-metadata.json`: a JSON list containing a dictionary for each matched Goodreads book. Example metadata keys are the year of publication (`yearFirstPublished`) and number of reviews (`numReviews`).

[Shakespeare and Company Project]: https://shakespeareandco.princeton.edu/

### Code requirements

1. This code needs Python 3. You can install the other dependencies with:
```
pip3 install -r requirements.txt
```

2. You will also need to download the
[Bayesian Core-Periphery Stochastic Block Models](https://github.com/ryanjgallagher/core_periphery_sbm)
and place the directory `core_periphery_sbm` into the current directory.

3. We additionally require version 1.1 of the data from the
[Shakespeare and Company Project](https://shakespeareandco.princeton.edu/about/data/).
Please download the following files and place them in the `data` directory:
- [`SCoData_books_v1.1_2021_01.json`](https://dataspace.princeton.edu/bitstream/88435/dsp016d570067j/3/): the Shakespeare and Company books dataset
- [`SCoData_members_v1.1_2021_01.json`](https://dataspace.princeton.edu/bitstream/88435/dsp01b5644v608/3/): the Shakespeare and Company members dataset
- [`SCoData_events_v1.1_2021_01.json`](https://dataspace.princeton.edu/bitstream/88435/dsp012n49t475g/3/): the Shakespeare and Company events dataset

We scraped the Goodreads metadata using the [Goodreads Scraper](https://github.com/maria-antoniak/goodreads-scraper).


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


### Reproducing the results in the article

All figures are saved in the `figures` subdirectory.

0. Scripts in the `connect-to-goodreads` directory perform the initial matching between SC and Goodreads books. These rely on the Goodreads API, which is now deprecated.

1. `popularity_plots.ipynb`:
implements the article section "Comparing Popularity in SC and Goodreads".

2. `plot-relative-popularity-by-year.py`:
plots the relative popularity by year across Goodreads and SC.

3. `compare-neighbor-distributions.py`:
implements the article section "Comparing reading patterns of poular books".

4. `core-periphery-books.ipynb`:
implements the network centrality analysis in the article section "Comparing network roles of popular books".

### Further example of how to use the graphs

Graphs are constructed for datasets from Shakespeare and Company and Goodreads.
Vertices correspond to books. Edges correspond to people: two books have an edge
between them if the same user interacted with both books.

Check out `example.py` for some sample code that shows how to:
1. Print summary statistics for the graphs
2. Find out information about a specific book in the graph

As an example, it shows that 'Hippolytus' by Euripides has an edge to only five other books
in the Shakespeare and Company graph but is connected to 68 books (many of which are 'classics') in the Goodreads graph.



