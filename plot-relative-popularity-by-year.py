from graph import get_goodreads_graph, get_sc_graph
import json
import numpy as np
import math

# don't let matplotlib use xwindows
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.pylab import savefig
import seaborn as sns
sns.set_style("ticks")
import pandas as pd

def plot_relative_popularity_by_year():

    # get the shakespeare and company graph
    sc_books_in_vertex_order, sc_book_to_vertex_index, sc_edge_to_weight, sc_vertex_to_neighbors, sc_n, sc_book_uri_to_num_events, sc_book_uri_to_text, sc_book_uri_to_year, sc_book_uri_to_title, sc_book_uri_to_author = get_sc_graph()

    # and now get the goodreads graph
    gr_books_in_vertex_order, gr_book_to_vertex_index, gr_edge_to_weight, gr_vertex_to_neighbors, gr_n, gr_book_id_to_num_ratings, gr_book_id_to_text = get_goodreads_graph()

    with open('data/goodreads-book-id-to-sc-uri_full-matching.json', 'r') as f:
        goodreads_book_id_to_sc_uri = json.load(f)

    # load newly scraped data
    df = pd.read_json('data/matched-goodreads-metadata.json')
    gr_book_id_to_scraped_num_reviews = {str(gr_id): num_reviews for gr_id, num_reviews in zip(df['bookID'], df['numReviews'])}
    gr_book_id_to_scraped_year = {str(gr_id): year for gr_id, year in zip(df['bookID'], df['yearFirstPublished'])}
    gr_book_id_to_scraped_title = {str(gr_id): title for gr_id, title in zip(df['bookID'], df['title'])}
    gr_book_id_to_scraped_author = {str(gr_id): author for gr_id, author in zip(df['bookID'], df['author'])}
    
    years = []
    titles = []
    authors = []
    gr_popularity_ratios = []
    sc_popularity_ratios = []
    gr_total_reviews = sum(gr_book_id_to_scraped_num_reviews.values())
    sc_total_borrows = sum(sc_book_uri_to_num_events.values())
    sc_texts = []
    for gr_book_id, sc_uri in goodreads_book_id_to_sc_uri.items():

        # some matched books don't have years in the dataset!!
        if gr_book_id not in gr_book_id_to_scraped_year:
            continue
        if math.isnan(gr_book_id_to_scraped_year[gr_book_id]):
            continue

        year = int(gr_book_id_to_scraped_year[gr_book_id])
        title = sc_book_uri_to_title[sc_uri]
        author = sc_book_uri_to_author[sc_uri]

        # skip super old books
        if year < 1800 or year > 1940:
            continue

        # sometimes popularity is zero--skip!!!
        if gr_book_id_to_scraped_num_reviews[gr_book_id] == 0:
            continue
        if sc_book_uri_to_num_events[sc_uri] == 0:
            continue


        #gr_text = gr_book_id_to_text[gr_book_id]
        #sc_text = sc_book_uri_to_text[sc_uri]
        sc_text = '{}\t{}'.format(gr_book_id_to_scraped_title[gr_book_id], gr_book_id_to_scraped_author[gr_book_id])

        # get relative popularity ratios
        gr_popularity_ratios.append(gr_book_id_to_scraped_num_reviews[gr_book_id] / gr_total_reviews)
        sc_popularity_ratios.append(sc_book_uri_to_num_events[sc_uri] / sc_total_borrows)

        years.append(year)
        titles.append(title)
        authors.append(author)

        sc_texts.append(sc_text)

    # now plot!
    log_ratios = [np.log(s / g) for s, g in zip(sc_popularity_ratios, gr_popularity_ratios)]

    point_types = []
    most_gr_examples = sorted(zip(log_ratios, years, sc_texts, [i for i in range(len(years))]), reverse=False)[:30]
    most_gr_idxs = [i for _, _, _, i in most_gr_examples]
    most_sc_examples = sorted(zip(log_ratios, years, sc_texts, [i for i in range(len(years))]), reverse=True)[:30]
    most_sc_idxs = [i for _, _, _, i in most_sc_examples]
    for i in range(len(log_ratios)):
        if i in most_gr_idxs:
            point_types.append('gr')
        elif i in most_sc_idxs:
            point_types.append('sc')
        else:
            point_types.append('normal')

    # '#86ceeb'
    color_dict = {'normal': '#b3cde3', 'sc': '#fc6b32', 'gr': '#13c28d'}
    marker_dict = {'normal': 'o', 'sc': 's', 'gr': 'D'}

    results = pd.DataFrame({'Year': years,
                        'log(SC/GR)': log_ratios,
                        'point_types': point_types
                       })
    plt.figure(figsize=(12.8, 4.8))
    ax = sns.scatterplot(data=results, x='Year', y='log(SC/GR)',
                         hue='point_types', palette=color_dict,
                         style='point_types', markers=marker_dict, legend=False)
    sns.despine()
    ax.set_xlim([1800,1941])
    ax.set_xlabel('Publication Year', fontsize=14)
    ax.set_ylabel('log(SC/GR)', fontsize=14)
    
    gr_legend = matplotlib.lines.Line2D([], [], color=color_dict['gr'], marker=marker_dict['gr'], linestyle='None',
                          markersize=10, label='Much more popular in Goodreads')
    sc_legend = matplotlib.lines.Line2D([], [], color=color_dict['sc'], marker=marker_dict['sc'], linestyle='None',
                              markersize=10, label='Much more popular in Shakespeare and Company')
    plt.legend(handles=[sc_legend, gr_legend])

    savefig('relative-popularity-by-year.png', bbox_inches='tight', dpi=300)
    plt.close()

    # print extreme books
    print('Most relatively popular in Goodreads:')
    for i, (ratio, year, title, author, text) in enumerate(sorted(zip(log_ratios, years, titles, authors, sc_texts), reverse=False)[:20]):
        print('\t{}\t{}\t{}\t{}'.format(i+1, year, title, author))
    print('Most relatively popular in Shakespeare and Company:')
    for i, (ratio, year, title, author, text) in enumerate(sorted(zip(log_ratios, years, titles, authors, sc_texts), reverse=True)[:20]):
        print('\t{}\t{}\t{}\t{}'.format(i+1, year, title, author))

if __name__ == '__main__':
    plot_relative_popularity_by_year()
