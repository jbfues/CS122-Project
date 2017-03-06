import sqlite3
from sys import path
path.append('~/CS122-Project/')
from util import break_string

db_file = '~/CS122-Project/database.sqlite3'

def search_rests(term):
    '''
    Returns list of restaurants 

    Input: term (str) the user input search term

    Returns: list of tuples of strings [(<url for restaurant view>,
             <name>, <address>), ... ]
    ''' 
    conn = sqlite3.connect(db_file)
    c = conn.cursor()



    conn.close()