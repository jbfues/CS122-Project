import numpy as np
import string
import json
import requests
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

CITY_API_ENDPOINT = 'https://data.cityofchicago.org/resource/cwig-ma7x.json'

def get_inspections(min_date = None):
    '''
    Retrieves all available food inspection data from the city data portal

    Input: min_date (string) in the form of a floating timestamp

            https://dev.socrata.com/docs/datatypes/floating_timestamp.html

    Output: list of dicts, where each dict represents an inspection
    '''
    req = CITY_API_ENDPOINT
    if min_date != None:
        # concatonate a query string to the request using SoQL
        # https://dev.socrata.com/docs/queries/
        req += '?$where=inspection_date > ' + min_date
    resp = requests.get(req)
    return resp.json()


def get_api_key(filename = 'yelp_api_key.json'):
    '''
    Retrieves API v2.0 key stored in a json file in the local directory
    (API uses OAuth 1.0a, xAuth protocal to authenitcate requests)

    API documentation:

        https://www.yelp.com/developers/documentation/v2/overview

    Input: .json filename

    Output: dictionary in the following form
        {
            "Consumer Key": <string>,
            "Consumer Secret": <string>,
            "Token": <string>,
            "Token Secret": <string>
        }
    '''
    json_file = open(filename)
    json_str = json_file.read()
    return json.loads(json_str)

def break_string(input_str):
    '''
    Takes a string and returns a list of words in the string.
    Inputs:
        One String
    Outputs:
        A list of words in the string
    '''
    raw_string = input_str.lower()
    string_list = raw_string.split()
    punc_list = list(string.punctuation)
    for item in string_list:
        for punc in punc_list:
            item = item.replace(punc, '')
    final_list = []
    for x in string_list:
        if x != "":
            final_list.append(x)
    return final_list

def get_name_words(inspection):
    '''
    Retrieves the words in the name of the restaurant from its inspection information.

    Inputs:
        inspection: a dictionary
    Outputs:
        A list of words in the name of the restaurant
    '''
    aka = break_string(inspection['aka_name'])
    dba = break_string(inspection['dba_name'])
    for word in aka:
        if word in dba:
            index = dba.index(word)
            dba.pop()
    return aka + dba 

class YelpHelper:
    '''
    A wrapper for the yelp library's client class 
    '''
    def __init__(self):
        key = get_api_key()
        auth = Oauth1Authenticator(
            consumer_key = key['Consumer Key'],
            consumer_secret= key['Consumer Secret'],
            token= key['Token'],
            token_secret= key['Token Secret']
            )
        self.client = Client(auth)

    def search_by_location(latitude, longitude, name, radius = 30, limit = 5):
        '''
        Inputs: latitude (number)
                longitude (number)
                name (string)
                radius (number)
                limit (number)

        Output: list of tuples of strings [(name, ID), ... ]
        '''
        params = {
            'term': name
            'limit': limit
            'radius_filter': radius
            }
        #resp is a SearchResponse object
        resp = client.search_by_coordinates(latitude, longitude, **params)
        results = []
        for b in resp.businesses: #iterate over business objects
            name = b.name.encode('utf-8')
            ID = b.id.encode('utf-8')
            results.append((name, ID))
        return results

    def search_by_id(ID):
        '''
        Input: unique yelp id 

        Output: Business object
        '''
        resp = client.get_business(ID)
        return resp.business



