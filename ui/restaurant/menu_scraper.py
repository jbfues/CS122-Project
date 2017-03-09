import sqlite3
from .util import YelpHelper
from .util import get_inspections_from_csv
from .util import get_possible_matches
from .util import pick_match
from .util import get_types
from .util import break_string
from .util import haversine
import jellyfish
import bs4
import urllib3
from urllib3 import PoolManager


def get_menu_items(yelp_id):
    '''
    Takes in a Yelp business id (as a string) 
    and returns a list of the items on the menu.
    '''

    # start by generating soup of the menu
    pm = PoolManager()
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
    c.execute(init_query, (license_number,))
    init_out = c.fetchone()
    init_lat = init_out[0]
    init_lon = init_out[1]
    if init_lat == None or init_lon == None:
        return nearby_restaurants
    # if we can, now we search restaurants
    query = "SELECT yelp_id FROM restaurants JOIN inspections AS a JOIN inspections AS b\
     ON restaurants.license = a.license AND restaurants.license = b.license\
      WHERE distance_between(a.longitude, a.latitude, b.longitude, b.latitude) <= 3200 AND a.license = ?\
       AND b.latitude IS NOT NULL AND b.longitude IS NOT NULL LIMIT 10"
    # collect the nearby restaurant data
    output = c.execute(query, (license_number,))
    for x in output.fetchall():
        if x[0] != None:
            nearby_restaurants.append(x[0])
    # return it
    return nearby_restaurants

def get_nearby_menus(license_number, db_filename):
    '''
    Takes the license number of a restaurant 
    and the name of the file with out database and returns 
    a dictionary of the nearby restaurants, indexed by yelp_id, 
    and their menus.
    '''
    # initialize the dictionary
    nearby_menus = {}
    # find the nearby restaurants
    nearby_restaurants = find_nearby_restaurants(license_number, db_filename)
    # find their menus
    for restaurant in nearby_restaurants:
        menu_items = get_menu_items(restaurant)
        nearby_menus[restaurant] = menu_items
    # return the completed dictionary
    return nearby_menus

def find_similar_restaurants(license_number, db_filename):
    '''
    Takes the license number and the filename of our database 
    and returns a list of restaurants that cover more than 60 percent of
    the available menu of the given restaurant.

    If we cannot find the menu of the restaurant, it simply returns a list of 
    nearby alternatives.

    Either way, the list will be a list of yelp_ids
    '''

    # connect to the database
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    # find the yelp_id of the given restaurant
    init_query = "SELECT yelp_id from restaurants WHERE license = ? LIMIT 1"
    init_output = c.execute(init_query, (license_number,))
    init_id = init_output.fetchone()[0]


    # return just nearby restaurants if we cannot find the menu
    if init_id == None:
        print("No menu found")
        return find_nearby_restaurants(license_number, db_filename)

    # get the menu from our restaurant
    init_menu = get_menu_items(init_id)
    # return just nearby restaurants if we get no menu results 
    if len(init_menu) == 0:
        print('No menu found')
        return find_nearby_restaurants(license_number, db_filename)

    # adjust the menu list
    menu_set = set()
    for item in init_menu:
        item_list = break_string(item)
        item_tup = tuple(item_list)
        menu_set.add(item_tup)
    # initialize the return list
    similar_restaurants = []
    # get the nearby menus
    nearby_menus = get_nearby_menus(license_number, db_filename)
    # find restaurants with similar menus
    for restaurant in nearby_menus:
        matches = 0
        menu_length = len(menu_set)
        menu = nearby_menus[restaurant]
        # select an item on the menu from the restaurant to match
        for menu_item in menu_set:
            my_len = len(menu_item)
            item_matches = 0
            # and check for it in the new menu
            for item in menu:
                item_words = break_string(item)
                for word in menu_item:
                    for x in item_words:
                        if jellyfish.jaro_winkler(x, word) >= .55:
                            item_matches += 1
            # if the item is on the new menu, add a match
            if item_matches/my_len >= .45:
                matches += 1
        # if 45 percent of the menu matches, add it to similar restaurants
        if matches/menu_length >= .45:
            similar_restaurants.append(restaurant)
    conn.close()
    # return the list of similar restaurants
    return similar_restaurants


