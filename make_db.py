import sqlite3
from util import YelpHelper
from util import get_inspections_from_csv
from util import get_possible_matches
from util import pick_match

def write_inspections_to_db(inspections_csv, c):
    '''
    Goes through all inspections, matches them to a unique yelp id 
    and writes them to SQL database 

    Input: 
        inspections_csv (str): filename for csv containing inspection data 
        cursor: sqlite3 Cursor object for database

    Returns: list of dicts representing unmatched inspections 
    '''
    yh = YelpHelper()
    inspections = get_inspections_from_csv(inspections_csv)
    for inspection in inspection:
        # . . . 
        candidates = get_possible_matches(inspection, yh)
        match = pick_match(inspection, candidates) #can also input block field
        # . . . 
    return [{}]

def create_tables(schema, filename):
    '''
    Creates tables designated in schema argument to sqlite file 

    Input: 
        schema (dict of lists)
            {
                <table name one>: [<field name one>, <field name two>, ... ]
                <table name two>: [<field name one>, <field name two>, ... ]
                .
                .
                .
            }
        filename (str): filename with .sqlite3 extension

    Returns: a sqlite3 Connection object
    '''
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    #######################################################
    # use c.execute(<command>) to create tables in database
    #######################################################


    #######################################################
    return c 

