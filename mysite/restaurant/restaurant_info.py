import sqlite3
from sys import path
path.append('~/CS122-Project/')
from util import YelpHelper

db_file = '~/CS122-Project/database.sqlite3'


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



    conn.close()

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