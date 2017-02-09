import numpy as np
import string
import json

def get_api_key(filename = 'yelp_api_key.json'):
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


        
