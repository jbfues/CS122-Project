import sqlite3
from .util import YelpHelper
from .get_recent_inspection import find_most_recent_inspection
from .menu_scraper import find_similar_restaurants
import smtplib

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
    c.execute(query, (license,))
    info = c.fetchone()
    r = {}
    r['name'] = info[0]
    r['address'] = info[1]
    r['date'] = inspection['inspection_date']
    r['type'] = inspection['inspection_type']
    r['results'] = inspection['results']
    r['violations'] = inspection['violations']
    r['risk'] = inspection['risk']
    r['license'] = license
    if info[2] != None:
        yh = YelpHelper()
        b = yh.search_by_id(info[2])
        r['rating'] = b.rating_img_url
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
    yelp_ids = find_similar_restaurants(license, db_file)
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    rest_tuples = []
    if yelp_ids:
        query = 'SELECT name, license, address FROM restaurants WHERE ' + ' OR '.join(
            ('yelp_id = ?' for ID in yelp_ids))
        c.execute(query, yelp_ids)
        restaurants = c.fetchall()
        for r in restaurants:
            rest_tuples.append((r[0], r[1], r[2]))
    conn.close()
    return rest_tuples


def add_to_list(license, email):
    '''
    Adds row to email_list table in database

    Inputs:
            license: (str) license number
            email: (str) email address
    '''
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('INSERT INTO email_list VALUES (?,?)', (license, email))
    #save the changes to db file
    conn.commit()
    conn.close()

def send_welcome_email(email):
    '''
    Sends welcome email to given email address
    Inputs:
        email: a string

    Email instructions courtesy of naelshiab.com
    '''

    my_serv = smtplib.SMTP('smtp.gmail.com', 587)
    my_serv.starttls()
    my_serv.login("safefoodchicago@gmail.com", "dontgettheruns")

    message = "Thank you for signing up for Safe Food Chicago email updates!\
     \n Best \n The Safe Food Chicago Team"

    my_serv.sendmail('safefoodchicago@gmail.com', email, message)
    my_serv.quit()
