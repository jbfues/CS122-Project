import sqlite3
import sys
from .index_search import search_by_words


db_file = '/home/student/CS122-Project/db.sql'

def search_rests(term):
    '''
    Returns list of restaurants 

    Input: term (str) the user input search term

    Returns: list of tuples of strings [(<url for restaurant view>,
             <name>, <address>), ... ]
    ''' 
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    rest_dicts = search_by_words(term, c) #name, license, address, zipcode, yelp_id
    rest_tuples = []
    for r in rest_dicts:
        rest_tuples.append((r['name'], r['license'], r['address']))
    conn.close()
    return rest_tuples