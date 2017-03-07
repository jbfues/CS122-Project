import sqlite3
from .util import break_string

def search_by_words(input_str, c):
    index_list = break_string(input_str, repetition='no')
    index_list = [word.lower() for word in index_list]
    if not index_list:
        return []
    query = 'SELECT license, COUNT(license) AS num FROM rest_index WHERE '
    list_where = []
    arguments = []
    for word in index_list:
        list_where.append('word = ? ')
        arguments.append(word)
    where_query = 'OR '.join(list_where)
    end_query = 'GROUP BY license ORDER BY num DESC LIMIT 10'
    final_query = query + where_query + end_query
    c.execute(final_query, arguments)
    all_licenses = c.fetchall()
    list_rest = []
    for license in all_licenses:
        lic = license[0]
        c.execute('SELECT * FROM restaurants WHERE license = ?', [lic])
        rest = c.fetchall()[0]
        rest_dict = {}
        rest_dict['name'] = rest[0]
        rest_dict['license'] = rest[1]
        rest_dict['address'] = rest[2]
        rest_dict['zipcode'] = rest[3]
        rest_dict['yelp_id'] = rest[4]
        list_rest.append(rest_dict)
    return list_rest