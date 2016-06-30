# _*_ coding:utf-8 _*_
from pymongo import MongoClient
import os
import codecs

from .db import *
from .tools import *
PATH = os.path.dirname(os.path.abspath(__file__))

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



