# _*_ coding:utf-8 _*_
import os, re
from functools import reduce
from .db import *
from .tools import *
from .filters import *

PATH = os.path.dirname(os.path.abspath(__file__))


def get_from_dict(dataDict, mapList):
    return reduce(lambda d, k: d[k], mapList, dataDict)


def set_in_dict(dataDict, mapList, value):
    get_from_dict(dataDict, mapList[:-1])[mapList[-1]] = value


def parse_config(config_dict):
    if config_dict['cacheData']:
        cache_data(config_dict)
        act_events = temp_events
    else:
        act_events = events

    results = dict(config_dict)
    config_dict = dict(config_dict)
    for i in range(0, len(results['items'])):
        unit_item = config_dict['items'][i]
        # filters
        if 'filter' in unit_item:
            for f in unit_item['filter']:
                r = filters(site_db, f)
                apply_info = f['apply']
                for k, v in apply_info.items():
                    conds = k.split('.')
                    set_in_dict(unit_item, conds, {"$in": r[v]})

        # actions
        if unit_item["action"] is "PV":
            r = PV(act_events, unit_item)
            results['items'][i]['result'] = r

        if unit_item["action"] is "UV":
            r = UV(act_events, unit_item)
            results['items'][i]['result'] = r

        if unit_item["action"] is "funnel":
            r = funnel(act_events, unit_item)
            results['items'][i]['result'] = r

        if unit_item["action"] is "ratio":
            r = ratio(act_events, unit_item)
            results['items'][i]['result'] = r

    temp_events.drop()

    return results
