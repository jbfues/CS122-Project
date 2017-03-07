import sqlite3
from sys import path
from .util import YelpHelper
from .get_recent_inspection import find_most_recent_inspection

db_file = '/home/student/CS122-Project/db.sql'

def get_info(license):
    '''
    Takes a license and returns a dictionary
    
    Returns: {
                'name': <dba name>,
                'address': <full address>,
                'rating': <rating image url>,
                'link': <link to yelp page>,
                'date': <date of inspection>,
                'type': <type of inspection>,
                'results': <results of inspection>,
                'violations': <violations from inspection>,
                'license': <license number>
            }
    '''
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    inspection = find_most_recent_inspection(license, c)
    query = "SELECT name, address, yelp_id FROM restaurants WHERE license = ?"
    c.execute(query, license)
    info = c.fetchone()
    r = {}
    r['name'] = info['name']
    r['address'] = info['address']
    r['date'] = inspection['inspection_date']
    r['type'] = inspection['inspection_type']
    r['results'] = inspection['results']
    r['violations'] = inspection['violations']
    r['license'] = license
    if info['yelp_id'] != None:
        yh = YelpHelper()
        b = yh.search_by_id(info['yelp_id'])
        r['rating'] = b.rating_image_url
        r['link'] = b.url 
    conn.close()
    return r 

def get_more(license):
    ''' 
    Input: license number 

    Returns: list of tuples of strings [(<url for restaurant view>,
             <name>, <address>), ... ] representing restaurants
            with similar menus.
    ''' 


    

def add_to_list(license, email):
    '''
    Adds row to email_list table in database

    Inputs:
            license: (str) license number
            email: (str) email address
    '''
    conn = sqlite3.connect(db_file)
    c = conn.cursor()


    #save the changes to db file
    conn.commit()
    conn.close()