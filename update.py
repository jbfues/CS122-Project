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

DICT_FIELDS = set(['address', 'aka_name', 'city', 'dba_name', 'facility_type',
    'inspection_date', 'inspection_id', 'inspection_type', 'latitude', 
    'license_', 'location', 'longitude', 'results', 'risk', 'state', 
    'violations', 'zip'])

def timestamp_to_date(timestamp):
    '''
    Convert a date in the form of a floating timestamp into a x/y/z form.

    Input: 
        timestamp (string): the timestamp to convert
    
    Returns: string
    '''
    year = timestamp[:4]
    if timestamp[5] == '0':
        month = timestamp[6]
    else:
        month = timestamp[5:7]
    if timestamp[8] == '0':
        day = timestamp[9]
    else:
        day = timestamp[8:10]
    date = month + '/' + day + '/' + year
    return date

def update_inspections_to_db(inspections, c):
    '''
    Goes through all inspections, matches them to a unique yelp id 
    and writes them to SQL database 

    Input: 
        inspections (list): list of dictionaries representing inspections
        c (cursor): sqlite3 Cursor object for database

    Returns: list of dicts representing unmatched inspections 
    '''
    yh = YelpHelper()
    types = get_types(inspections)
    unmatched = []
    for inspection in inspections:
        if inspection['location']:
            inspection['location'] = str((inspection['location']['coordinates'][1
                ], inspection['location']['coordinates'][0]))
        if inspection['inspection_date']:
            inspection['inspection_date'] = timestamp_to_date(inspection[
                'inspection_date'])
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

def leap_year(year):
    '''
    Check whether a year number corresponds to leap year or not.

    Input: 
        year: int

    Returns: Boolean
    '''
    if year % 4 != 0:
        return False
    if year % 100 != 0:
        return True
    if year % 400 == 0:
        return True
    return False

def next_day(date_tuple):
    '''
    Finds the tuple representing the day coming after another one given as a 
    tuple of the form (year, month, day).

    Input: 
        date_tuple: tuple

    Returns: tuple
    '''
    year = date_tuple[0]
    month = date_tuple[1]
    day = date_tuple[2] + 1
    if day == 32:
        month += 1
        day = 1
    if day == 31:
        if month == 4 or month == 6 or month == 9 or month == 11:
            month += 1
            day = 1
    if day == 30:
        if month == 2:
            month += 1
            day = 1
    if day == 29:
        if month ==2:
            if not leap_year(year):
                month += 1
                day = 1
    if month == 13:
        year += 1
    return (year, month, day)

def update(db_file):
    '''
    Find the most recent inspection in the database and add to the database 
    every inspections from the following day and after (maximum 1000).

    Input: 
        db_file (str): name of the sql database
    '''
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
    date_tuple = next_day(date_tuple)
    year = str(date_tuple[0])
    if date_tuple[1] < 10:
        month = '0' + str(date_tuple[1])
    else:
        month = str(date_tuple[1])
    if date_tuple[2] < 10:
        day_number = '0' + str(date_tuple[2])
    else:
        day_number = str(date_tuple[2])
    min_date = '"' + year + '-' + month + '-' + day_number + 'T00:00:00"'
    inspections = get_inspections_from_api(min_date)
    for inspection in inspections:
        if len(inspection) != 17:
            for insp_field in DICT_FIELDS:
                if insp_field not in inspection:
                    inspection[insp_field] = ''
    update_inspections_to_db(inspections, c)
    conn.commit()
    conn.close()