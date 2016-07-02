# _*_ coding:utf-8 _*_
from pymongo import MongoClient
import datetime

db_path = '10.8.8.111:27017'
db = MongoClient(db_path)['eventsV35']
site_db = MongoClient(db_path)['onions']

events = db['eventV35']
temp_events = db['tempEvents']


def cache_data(config_dict):
    temp_events.drop()
    union_query = {
        "eventKey": {"$in": []},
        "serverTime": {"$lt": datetime.datetime(1970, 1, 1), "$gte": datetime.datetime.now()}
    }
    for each in config_dict['items']:
        if each['action'] is "PV" or each['action'] is "UV":
            if 'eventKey' in each['config'] and type(each['config']['eventKey']) is str:
                union_query['eventKey']['$in'].append(each["config"]["eventKey"])
            elif 'eventKey' in each['config'] and '$in' in each['config']['eventKey']:
                union_query['eventKey']['$in'] += each['config']['eventKey']['$in']

        if each['action'] is "funnel":
            union_query['eventKey']['$in'] += each['sequence']
            if each['haveChild']:
                child_list = each['funnelSettings']['child']
                union_query['eventKey']['$in'] += [k[1] for k in child_list]

        if each['action'] is 'ratio':
            if 'eventKey' in each['numerator']['config'] and type(each['numerator']['config']['eventKey']) is str:
                union_query['eventKey']['$in'].append(each['numerator']["config"]["eventKey"])
            elif 'eventKey' in each['numerator']['config'] and '$in' in each['numerator']['config']['eventKey']:
                union_query['eventKey']['$in'] += each['numerator']['config']['eventKey']['$in']

            if 'eventKey' in each['denominator']['config'] and type(each['denominator']['config']['eventKey']) is str:
                union_query['eventKey']['$in'].append(each['denominator']["config"]["eventKey"])
            elif 'eventKey' in each['denominator']['config'] and '$in' in each['denominator']['config']['eventKey']:
                union_query['eventKey']['$in'] += each['denominator']['config']['eventKey']['$in']

        if 'serverTime' in each['config'] and '$gte' in each['config']['serverTime']:
            if each['config']['serverTime']['$gte'] < union_query['serverTime']['$gte']:
                union_query['serverTime']['$gte'] = each['config']['serverTime']['$gte']

        if 'serverTime' in each['config'] and '$lt' in each['config']['serverTime']:
            if each['config']['serverTime']['$lt'] > union_query['serverTime']['$lt']:
                union_query['serverTime']['$lt'] = each['config']['serverTime']['$lt']

    if len(union_query['eventKey']['$in']) == 0:
        union_query.pop('eventKey', None)

    if union_query['serverTime']['$lt'] == datetime.datetime(1970, 1, 1):
        union_query.pop('serverTime')
    elif union_query['serverTime']['$gte'] > union_query['serverTime']['$lt']:
        union_query['serverTime'].pop('$gte')

    if "serverTime" in union_query.keys() and len(union_query['serverTime']) == 0:
        union_query.pop('serverTime', None)
    print(union_query)
    x = events.find(union_query)
    temp_events.insert_many(list(x))
