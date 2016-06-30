# _*_ coding:utf-8 _*_
from pymongo import MongoClient
import os
import datetime
import codecs
PATH = os.path.dirname(os.path.abspath(__file__))

db_path = '10.8.8.111:27017'

db = MongoClient(db_path)['eventsV35']
events = db['eventV35']
temp_events = db['tempEvents']

config_path = PATH +'/examples/sample.datacfg'

f = codecs.open(config_path, 'r', 'utf8').read()

x = eval(f)

def cache_data(config_dict):
    temp_events.drop()
    union_query = {
        "eventKey": {"$in": []},
        "serverTime": {"$lt": datetime.datetime(1970,1,1), "$gte": datetime.datetime.now()}
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

        if 'serverTime' in each['config'] and '$gte' in each['config']['serverTime']:
                if each['config']['serverTime']['$gte'] < union_query['serverTime']['$gte']:
                    union_query['serverTime']['$gte'] = each['config']['serverTime']['$gte']

        if 'serverTime' in each['config'] and '$lt' in each['config']['serverTime']:
            if each['config']['serverTime']['$lt'] > union_query['serverTime']['$lt']:
                union_query['serverTime']['$lt'] = each['config']['serverTime']['$lt']

    if len(union_query['eventKey']['$in']) == 0:
        union_query.pop('eventKey', None)

    if union_query['serverTime']['$lt'] == datetime.datetime(1970,1,1):
        union_query.pop('serverTime')
    elif union_query['serverTime']['$gte'] > union_query['serverTime']['$lt']:
        union_query['serverTime'].pop('$gte')

    if len(union_query['serverTime']) == 0:
        union_query.pop('serverTime', None)
    print(union_query)
    x = events.find(union_query)
    temp_events.insert_many(list(x))



def PV(col, action_config):
    if action_config['haveGroup']:
        pipeline = [
            {"$match": action_config['config']},
            {"$group": {"_id": action_config['PVSettings']['groupBy'], "count": {"$sum": 1}}}
        ]
        return list(col.aggregate(pipeline))
    else:
        return col.count(action_config["config"])

def UV(col, action_config):
    return len(col.distinct(action_config["userType"], action_config["config"]))

def funnel(col, action_config):
    result = []
    PV_result = []
    sequence = action_config['sequence']
    i = 0
    query = dict(action_config['config'])
    query["eventKey"] = sequence[i]
    step_users = col.distinct(action_config['userType'], query)
    result.append(len(step_users))

    if action_config['havePV'] and 0 in action_config['funnelSettings']['PV']:
        step_pv = col.count(query)
        PV_result.append((0, step_pv))

    for i in range(1, len(sequence)):
        query["eventKey"] = sequence[i]
        query[action_config["userType"]] = {"$in": step_users}
        if action_config['havePV'] and i in action_config['funnelSettings']['PV']:
            step_pv = col.count(query)
            PV_result.append((i, step_pv))
        step_users = col.distinct(action_config['userType'], query)
        result.append(len(step_users))

    return (tuple(result), tuple(PV_result))


def parse_config(config_dict):
    if config_dict['cacheData']:
        cache_data(config_dict)
        act_events = temp_events
    else:
        act_events = events

    results = dict(config_dict)
    for i in range(0, len(results['items'])):
        unit_item = results['items'][i]
        if unit_item["action"] is "PV":
            r = PV(act_events, unit_item)
            results['items'][i]['result'] = r

        if unit_item["action"] is "UV":
            r = UV(act_events, unit_item)
            results['items'][i]['result'] = r

        if unit_item["action"] is "funnel":
            r = funnel(act_events, unit_item)
            results['items'][i]['result'] = r

    temp_events.drop()

    return results



