import sqlite3
from util import YelpHelper
from util import get_inspections_from_csv
from util import get_possible_matches
from util import pick_match
from util import get_types
from util import break_string

def get_inspections(license_number, c):
    '''
    Gathers all inspections for a given restaurant.
    Inputs:
        license_number: a string
        c: a sqlite cursor
    Outputs:
        a list of tuples returned from the sqlite database
    '''

    query = "SELECT license, inspection_id, risk, inspection_date, inspection_type, results, violations, latitude, longitude \
    FROM inspections WHERE license = ?"
    return c.execute(query, license_number).fetchall()


def find_most_recent_inspection(license_number, c):
    '''
    Finds the most recent inspection for a restaurant.
    Inputs:
        license_number: a string
        c: a sqlite cursor
    Outputs:
        a dict representing the most recent inspection
    '''
    # get the inspections
    rest_inspections = get_inspections(license_number, c)

    # find the most recent one
    first = True
    best_inspection = None
    for inspection in rest_inspections:
        if first:
            best_inspection = inspection
            first = False
        else:
            best_date_string = best_inspection['inspection_date']
            curr_date_string = inspection['inspection_date']
            best_list = best_date_string.split('/')
            curr_list = curr_date_string.split('/')
            best_list = list(map(int, best_list))
            curr_list = list(map(int, best_list))
            if curr_list[2] > best_list[2]:
                best_inspection = inspection
            else:
                if curr_list[1] > best_list[1]:
                    best_inspection = inspection
                else:
                    if curr_list[0] > best_list[0]:
                        best_inspection = inspection
    # build the return dict
    inspection_dict = {}
    inspection_dict['license_'] = best_inspection['license']
    inspection_dict['inspection_id'] = best_inspection['inspection_id']
    inspection_dict['risk'] = best_inspection['risk']
    inspection_dict['inspection_date'] = best_inspection['inspection_date']
    inspection_dict['inspection_type'] = best_inspection['inspection_type']
    inspection_dict['results'] = best_inspection['results']
    inspection_dict['violations'] = best_inspection['violations']
    inspection_dict['latitude'] = best_inspection['latitude']
    inspection_dict['longitude'] = best_inspection['longitude']

    return inspection_dict




