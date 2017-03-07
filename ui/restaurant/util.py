import numpy as np
import string
import json
import requests
import re
import jellyfish
import csv
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
from math import radians, cos, sin, asin, sqrt

CITY_API_ENDPOINT = 'https://data.cityofchicago.org/resource/cwig-ma7x.json'
KEYWORDS = ['nursing', 'day care', 'school', 'bakery', 'deli', 
            'restaurant', 'pub', 'cafe', 'coffee', 'college',
            'daycare', 'food pantry', 'truck', 'shelter', 'tevern',
            'pub', 'tea', 'bar', 'icecream', 'gelato', 'shop', 'theater']

def get_types(inspections):
    '''
    Takes a list of dicts representing inspections and returns a list 
    of facility_type values that are deemed in the focus of the project.
    '''
    t = set()
    for inspection in inspections:
        t.add(inspection['facility_type'])
    types = set()
    for val in t:
        for word in KEYWORDS:
            if word in val.lower():
                types.add(val)
    return list(types)


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
        header = [h.lower().replace(' ', '_').rstrip('#') for h in header]
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


def get_api_key(filename = '/home/student/CS122-Project/yelp_api_key.json'):
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

def break_string(input_str, repetition='yes'):
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
        if repetition == 'yes' or x not in final_list:
            if x != "":
                if repetition == 'no':
                    final_list.append(x.strip('"'))
                else:
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

def address_to_tuple(address):
    '''
    Takes an address string and returns a corresponding 
    (<number>, <street name>) tuple 

    If address string does not start with a sequence of digits, then
    num will be '' and street will be the whole address string.

    Inputs: address (str) e.g. "140 New Montgomery St"

    Returns: (tuple of strings) e.g. ('140', 'New Montgomery St')
    '''
    m = re.match(r'([\d-]*)([^\d-].*)$', address)
    num = m.group(1)
    street = m.group(2).strip().lower()
    return (num, street)

def get_possible_matches(inspection, yh, radius = 150, limit = 5):
    '''
    Takes a dict representing an inspection and a YelpHelper and
    returns a list of dicts representing possible yelp matches 
    '''
    latitude = inspection['latitude']
    longitude = inspection['longitude']
    name = inspection['dba_name']
    matches = yh.search_by_location(latitude, longitude, name, radius, limit)
    return matches 

def pick_match(inspection, candidates):
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
    Returns: a dict from candidates if a match is found, None otherwise
    '''
    #Get information about the inspection
    inspec_name = inspection['dba_name'].lower()
    inspec_zip = str(inspection['zip'])
    inspec_street_num, inspec_street_name = address_to_tuple(inspection['address'])

    best_match = None
    best_match_name_jw = 0
    best_match_street_jw = 0
    best_match_num_jw = 0
    first = True
    #Iterate over candidates to find the best match:
    if candidates:
        for candidate in candidates:
            if candidate['zip'] == inspec_zip:
                cand_name = candidate['name'].lower()
                cand_st = candidate['street name'].lower()
                cand_st_num = candidate['street number']
                curr_name_jw = jellyfish.jaro_winkler(cand_name, inspec_name)
                curr_st_jw = jellyfish.jaro_winkler(cand_st, inspec_street_name)
                curr_num_jw = jellyfish.jaro_winkler(cand_st_num, inspec_street_num) 
                if first:
                    if curr_name_jw >= .775:
                        if curr_st_jw >= .775:
                            if curr_num_jw >= .775:
                                best_match = candidate
                                best_match_name_jw = curr_name_jw
                                best_match_street_jw = curr_st_jw
                                best_match_num_jw = curr_num_jw
                                first = False
                else:
                    if curr_name_jw >= .775:
                        if curr_st_jw >= .775:
                            if curr_num_jw >= .775:
                                curr_sum = curr_name_jw + curr_st_jw + curr_num_jw
                                best_sum = best_match_name_jw + best_match_street_jw + best_match_num_jw
                                if curr_sum > best_sum:
                                    best_match = candidate
                                    best_match_name_jw = curr_name_jw
                                    best_match_street_jw = curr_st_jw
                                    best_match_num_jw = curr_num_jw
    return best_match


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points 
    on the earth (specified in decimal degrees)

    Taken from Programming Assignment 3, courses.py, from 
    CS122 at the University of Chicago, Winter 2017.
    '''
    # ensure that the values are decimal degrees, not strings. 
    lon1 = float(lon1)
    lon2 = float(lon2)
    lat1 = float(lat1)
    lat2 = float(lat2)
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m


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

    def search_by_location(self, latitude, longitude, name, radius = 30, limit = 5):
        '''
        Inputs: latitude (str)
                longitude (str)
                name (str)
                radius (number)
                limit (number)

        candidates: list of dicts representing businesses
        '''
        #resp is a SearchResponse object
        resp = self.client.search_by_coordinates(latitude, longitude, term = name,
                    limit = limit, radius_filter = radius)
        results = []
        for business in resp.businesses: #iterate over business objects
            try:
                address = business.location.address[0]
                address = address_to_tuple(str(address).strip("b").strip("'"))
                b = {
                    'name': str(business.name).strip("b").strip("'"), 
                    'street number': address[0], 
                    'street name': address[1], 
                    'zip': str(business.location.postal_code).strip("b").strip("'"),
                    'yelp_id': str(business.id).strip("b").strip("'")
                    }
                results.append(b)
            except:
                pass
        return results

    def search_by_id(ID):
        '''
        Input: unique yelp id 

        Output: Business object
        '''
        resp = self.client.get_business(ID)
        return resp.business



