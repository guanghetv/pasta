# _*_ coding:utf-8 _*_

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
