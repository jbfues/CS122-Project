import sqlite3
from util import YelpHelper
from util import get_inspections_from_csv
from util import get_possible_matches
from util import pick_match
from util import get_types
from util import break_string

def write_inspection(i, c):
    '''
    Writes inspection data into inspections table 

    Columns are (inspection_id, risk, inspection_date,
                     inspection_type, results, violations, latitude,
                      longitude)
    '''
    c.execute("INSERT INTO inspections VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                        (i['license_'], i['inspection_id'], i['risk'], 
                            i['inspection_date'], i['inspection_type'], 
                            i['results'], i['violations'], i['latitude'], i['longitude']))

def make_index(c):
    c.execute('SELECT license, name, address, zipcode FROM restaurants')
    list_rest = c.fetchall()
    for license, name, address, zipcode in list_rest:
        to_index = name + ' ' + address + ' ' + zipcode
        index_list = break_string(to_index, repetition='no')
        index_list = [word.lower() for word in index_list]
        for index_word in index_list:
            c.execute('INSERT INTO rest_index VALUES (?, ?)', (license, index_word))

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
    for inspection in inspections:
        if inspection['facility_type'] in types and inspection['license_'
                ] != '' and inspection['license_'] != 0:
            inDB = c.execute("SELECT * FROM restaurants WHERE license=:license_",
                 inspection)
            if not inDB.fetchall():
                if inspection["latitude"] and inspection["longitude"]:
                    candidates = get_possible_matches(inspection, yh)
                    match = pick_match(inspection, candidates) #can take block field
                    if match != None:
                        c.execute("INSERT INTO restaurants VALUES (?, ?, ?, ?, ?)", 
                            (inspection['dba_name'], inspection['license_'], 
                                inspection['address'], inspection['zip'], 
                                match['yelp_id']))
                    else: 
                        unmatched.append(inspection)
                else:
                    unmatched.append(inspection)
            write_inspection(inspection, c)
            c.connection.commit()
    for inspection in unmatched:
        inDB = c.execute("SELECT * FROM restaurants WHERE license=:license_",
            inspection)
        if not inDB.fetchall():
            query = ("INSERT INTO restaurants (name, license, address, " + 
                "zipcode) VALUES (?, ?, ?, ?)")
            c.execute(query, (inspection['dba_name'], inspection['license_'], 
                inspection['address'], inspection['zip']))
    make_index(c)
    return unmatched

def create_tables(schema, c):
    '''
    Creates tables designated in schema argument to sqlite file 

    Inputs: 
        schema (dict of lists of tuples)
            {
                <table name one>: [(<field name one>, <type 1>), (<field name two>,<type 1>), ... ]
                <table name two>: [(<field name one>, <type 1>), (<field name two>,<type 1>), ... ]
                .
                .
                .
            }
        c (Cursor): a sqlite3 Cursor object for interacting with database

    Returns: None
    '''

    #######################################################
    # use c.execute(<command>) to create tables in database
    #######################################################
    for table in schema:

        # First part of the final query.
        query = "CREATE TABLE " + str(table) + " ("

        # Create the second part of the query by joining strings.
        query_list = []
        for field in schema[table]:
            field_string = str(field[0]) + " " + str(field[1])
            query_list.append(field_string)
        query_bis = ", ".join(query_list)
        
        # Put it all together.
        query = query + query_bis + ")"
        c.execute(query)

    #######################################################

def make_db_from(inspections_csv, db_file):
    '''
    For each applicable inspection, finds corresponding yelp id if possible 
    and writes information for restaurants and inspections to relevant tables.

    Inputs: 
        inspections_csv: (str) filename of inspections csv  from city data portal
        db_file: (str) filename of sqlite3 database
    '''
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    schema = {
            'restaurants': [('name', 'text'),
                            ('license', 'text'),
                            ('address', 'text'),
                            ('zipcode', 'text'),
                            ('yelp_id', 'text')],
            'inspections': [('license', 'text'),
                            ('inspection_id', 'text'),
                            ('risk', 'text'),
                            ('inspection_date', 'text'),
                            ('inspection_type', 'text'),
                            ('results', 'text'),
                            ('violations', 'text'),
                            ('latitude', 'text'),
                            ('longitude', 'text')],
            'rest_index':  [('license', 'text'),
                            ('word', 'text')]
            }
    create_tables(schema, c)
    write_inspections_to_db(inspections_csv, c)
    #save the changes to db file
    conn.commit()
    conn.close()


