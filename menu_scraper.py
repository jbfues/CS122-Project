import sqlite3
from util import YelpHelper
from util import get_inspections_from_csv
from util import get_possible_matches
from util import pick_match
from util import get_types
from util import break_string
from util import haversine
import jellyfish
import bs4
import urllib3


def get_menu_items(yelp_id):
    '''
    Takes in a Yelp business id (as a string) 
    and returns a list of the items on the menu.
    '''

    # start by generating soup of the menu
    pm = urllib3,PoolManager()
    rest_url = "http://www.yelp.com/menu/" + yelp_id
    html_data = pm.urlopen(url = rest_url, method = "GET").data
    my_soup = bs4.BeautifulSoup(html_data, 'lxml')

    menu_item_list = []

    # next, search through the menu for all the items
    init_items = my_soup.find_all('h4')
    for item in init_items:
        item_links = item.find_all('a')
        if len(item_links) > 0:
            menu_item_list.append(item_links[0].text)
        else:
            menu_item_list.append(item.text.strip())

    return menu_item_list

def find_nearby_restaurants(license_number, db_filename):
    '''
    Takes a restaurant's license number (string) and uses it to find 
    nearby restaurants in the database. The database is found in 
    the file db_filename.

    Returns a list of a maximum of 5 yelp_ids of nearby restaurants
    '''

    conn = sqlite3.connect(db_filename)
    conn.create_function('distance_between', 4, haversine)
    c = conn.cursor()
    nearby_restaurants = []
    # check if we have the location information
    init_query = "SELECT latitude, longitude FROM inspections where license = ? LIMIT 1"
    init_out = c.execute(init_query, license_number)
    init_lat = init_out.fetchone()['latitude']
    init_lon = init_out.fetchone()['longitude']
    if init_lat == None or init_lon == None:
        return nearby_restaurants
    # if we can, now we search restaurants
    query = "SELECT yelp_id FROM restaurants JOIN inspections AS a JOIN inspections AS b\
     ON restaurants.license = a.license AND restaurants.license = b.license\
      WHERE distance_between(a.longitude, a.latitude, b.longitude, b.latitude) <= 1600 AND a.license = ?\
       LIMIT 5"
    # collect the nearby restaurant data
    output = c.execute(query, license_number)
    for x in output.fetchall():
        nearby_restaurants.append(x['yelp_id'])
    # return it
    return nearby_restaurants
