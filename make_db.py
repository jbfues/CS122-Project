import sqlite3
from util import YelpHelper
from util import get_inspections_from_csv
from util import get_possible_matches
from util import pick_match

def write_inspection(i, c):
    '''
    Writes inspection data into inspections table 

    Columns are (inspection_id, risk, inspection_date,
                     inspection_type, results, violations)
    '''
    c.execute("INSERT INTO inspections VALUES (?, ?, ?, ?, ?, ?)", 
                        (i['inspection_id'], i['risk'], i['inspection_date'], 
                            i['inspection_type'], i['results'], i['violations']))

def write_inspections_to_db(inspections_csv, c):
    '''
    Goes through all inspections, matches them to a unique yelp id 
    and writes them to SQL database 

    Input: 
        inspections_csv (str): filename for csv containing inspection data 
        c (cursor): sqlite3 Cursor object for database

    Returns: list of dicts representing unmatched inspections 
    '''
    yh = YelpHelper()
    inspections = get_inspections_from_csv(inspections_csv)
    types = get_types(inspections)
    unmatched = []
    for inspection in inspection:
        if inspection['facility_type'] in types:
            inDB = c.execute("SELECT * FROM restaurants WHERE license=:license_",
                 inspection)
            if not inDB and inspection['license_'] != '':
                candidates = get_possible_matches(inspection, yh)
                match = pick_match(inspection, candidates) #can take block field
                if match != None:
                    c.execute("INSERT INTO restaurants VALUES (?, ?, ?, ?)", 
                        (match['name'], inspection['license_'], 
                            inspection['address'], match['yelp_id']))
                else unmatched.append(inspection)
            write_inspection(inspection)
    return unmatched

def create_tables(schema, filename):
    '''
    Creates tables designated in schema argument to sqlite file 

    Input: 
        schema (dict of lists of tuples)
            {
                <table name one>: [(<field name one>, <type 1>), (<field name two>,<type 1>), ... ]
                <table name two>: [(<field name one>, <type 1>), (<field name two>,<type 1>), ... ]
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

