import re
import sqlite3
from util import YelpHelper
from util import get_possible_matches
from util import pick_match
from util import get_types
from util import break_string
from util import get_inspections_from_api
from make_db import write_inspection
from make_db import make_index

def update_inspections_to_db(inspections, c):
    '''
    Goes through all inspections, matches them to a unique yelp id 
    and writes them to SQL database 

    Input: 
        inspections_csv (str): filename for csv containing inspection data 
        c (cursor): sqlite3 Cursor object for database

    Returns: list of dicts representing unmatched inspections 
    '''
    yh = YelpHelper()
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

def update(db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    date_tuple = (0,0,0)
    c.execute('SELECT inspection_date FROM inspections')
    list_dates = c.fetchall()
    for date in list_dates:
        day_list = re.findall('[0-9]+', date[0])
        day = (int(day_list[2]), int(day_list[0]), int(day_list[1]))
        if day > date_tuple:
            date_tuple = day
    year = str(date_tuple[0])
    if date_tuple[1] < 10:
        month = '0' + str(date_tuple[1])
    else:
        month = str(date_tuple[1])
    if date_tuple[2] < 10:
        day_number = '0' + str(date_tuple[2])
    else:
        day_number = str(date_tuple[2])
    min_date = year + '-' + month + '-' + day_number + 'T00:00:00'
    inspections = get_inspections_from_api(min_date)
    update_inspections_to_db(inspections, c)
    conn.commit()
    conn.close()