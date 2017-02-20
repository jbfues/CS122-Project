import numpy as np
import string
import json
import requests
import re
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator

CITY_API_ENDPOINT = 'https://data.cityofchicago.org/resource/cwig-ma7x.json'

def get_inspections_from_csv(filename):
    '''
    Input: csv file downloaded from city data portal at 
           https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5

    Returns: list of dicts, where each dict represents an inspection and has 
            keys for the field names of the city dataset
    '''
    with open(filename) as f:
        reader = csv.reader(f, skipinitialspace=True)
        header = next(reader)
        inspections = [dict(zip(header, row)) for row in reader]
    return inspections  


def get_inspections_from_api(min_date = None):
    '''
    Retrieves all available food inspection data from the city data portal

    **NOTE**: There appears to be a maximum of 1000 inspections returned,
              so use get_inspections_from_csv() for intitial data pull.

    Input: min_date (string) in the form of a floating timestamp

            https://dev.socrata.com/docs/datatypes/floating_timestamp.html

    Returns: list of dicts, where each dict represents an inspection and has 
            keys for the fieldnames from the city dataset
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
            "Consumer Key": <str>,
            "Consumer Secret": <str>,
            "Token": <str>,
            "Token Secret": <str>
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

def get_name_words(inspection, match = {}):
    '''
    Retrieves the words in the name of the restaurant from its 
    inspection information and its yelp page (if applicable)

    Inputs:
        inspection (dict)
        match (dict, optional): contains the yelp data for the restaurant 
    Outputs:
        A list of words in the name of the restaurant
    '''
    aka = break_string(inspection['aka_name'])
    dba = break_string(inspection['dba_name'])
    for word in aka:
        if word in dba:
            index = dba.index(word)
            dba.pop(index)
    result = aka + dba
    if match:
        name = break_string(match['name'])
        for word in result:
            if word in name:
                index = name.index(word)
                name.pop(index)
        result += name 
    return result  

def get_possible_matches(inspection, yh):
    '''
    Takes a dict representing an inspection and a YelpHelper and
    returns a list of dicts representing possible yelp matches 
    '''
    return {[]}

def pick_match(inspection, candidates, block = None):
    '''
    Searches for the restaurant from an inspection in a list of
    restaurants from yelp

    Inputs:
        inspection: dict with indices for each field name from city dataset
        candidates: list of dicts in the form of
                        {
                            'name': <string>, 
                            'street number': <string>, 
                            'street name' <string>,
                            'zip': <string>
                            'yelp_id: <string>
                         }
        block (optional): a field by which to automatically reject candidates
                          if said field does not match exactly

    Returns: a dict from candidates if a match is found, None otherwise
    '''
    return {} 

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
        self.p = re.compile(r'\d*')

    def search_by_location(latitude, longitude, name, radius = 30, limit = 5):
        '''
        Inputs: latitude (number)
                longitude (number)
                name (string)
                radius (number)
                limit (number)

        candidates: list of dicts representing businesses
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
            address = business.location.city.encode('utf-8')
            m = self.p.match(address)
            num = m.group(1)
            street = m.group(2).strip()
            b = {
                'name': b.name.encode('utf-8'), 
                'street number': num, 
                'street name': street, 
                'zip': business.location.postal_code.encode('utf-8'),
                'yelp_id': b.id.encode('utf-8')
                }
            results.append(b)
        return results

    def search_by_id(ID):
        '''
        Input: unique yelp id 

        Output: Business object
        '''
        resp = client.get_business(ID)
        return resp.business



