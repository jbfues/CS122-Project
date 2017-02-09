import numpy as np
import string
import json
import requests

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



