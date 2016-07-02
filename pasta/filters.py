# _*_ coding:utf-8 _*_
from bson.objectid import ObjectId


class Course:
    def __init__(self, course_db, publisher="人教版", subject="math", status="published"):
        self.chapters = []
        self.themes = []
        x = course_db['chapters'].find({"publisher": publisher, "subject": subject, "status": status})
        for chapter in x:
            unit_chapter = {
                "id": chapter['_id'],
                "publisher": chapter['publisher'],
                "semester": chapter['semester'],
                "subject": chapter['subject'],
                "name": chapter['name'],
                "status": chapter['status'],
                "normalTheme": [],
                "examTheme": [],
                "payTopic": [],
                "freeTopic": [],
                "typeTopic": {
                    "A": [],
                    "B": [],
                    "C": [],
                    "D": [],
                    "E": [],
                    "I": [],
                    "S": []
                },
                "statusTopic": {
                    "published": [],
                    "unpublished": []
                }
            }
            for theme in chapter['themes']:
                if theme['type'] == 'normal':
                    unit_chapter['normalTheme'].append(theme['_id'])
                if theme['type'] == 'exam':
                    unit_chapter['examTheme'].append(theme['_id'])

                unit_theme = {
                    "id": theme['_id'],
                    "payTopic": [],
                    "freeTopic": [],
                    "typeTopic": {
                        "A": [],
                        "B": [],
                        "C": [],
                        "D": [],
                        "E": [],
                        "I": [],
                        "S": []
                    },
                    "statusTopic": {
                        "published": [],
                        "unpublished": []
                    }
                }

                for topic in theme['topics']:
                    x_topic = course_db['topics'].find_one({"_id": topic})
                    if x_topic != None:
                        if x_topic['pay']:
                            unit_chapter['payTopic'].append(x_topic["_id"])
                            unit_theme['payTopic'].append(x_topic['_id'])
                        else:
                            unit_chapter['freeTopic'].append(x_topic["_id"])
                            unit_theme['freeTopic'].append(x_topic["_id"])

                        unit_chapter['typeTopic'][x_topic["type"]].append(x_topic["_id"])
                        unit_theme['typeTopic'][x_topic['type']].append(x_topic["_id"])

                        unit_chapter['statusTopic'][x_topic['status']].append(x_topic['_id'])
                        unit_theme['statusTopic'][x_topic['status']].append(x_topic["_id"])

                self.themes.append(unit_theme)
            self.chapters.append(unit_chapter)


def payable_course(course_db, publisher="人教版", subject="math", status="published"):
    c = Course(course_db, publisher="人教版", subject="math", status="published")
    result = {
        "chapter_id": [],
        "theme_id": [],
        "topic_id": []
    }
    for chapter in c.chapters:
        if len(chapter['payTopic']) > 0:
            result["chapter_id"].append(str(chapter['id']))

    for theme in c.themes:
        if len(theme['payTopic']) > 0:
            result['theme_id'].append(str(theme['id']))
            result['topic_id'] += [str(x) for x in theme['payTopic']]

    return result


def full_topics(course_db, topic_list):
    list_id = [ObjectId(x) for x in topic_list]
    x = course_db['topics'].find({"_id": {"$in": list_id}})
    result = []
    for topic in x:
        full_flag = False
        if 'modules' in topic:
            for module in topic['modules']:
                if 'hyperVideo' in module and 'practice' in module:
                    if len(module['practice']['levels']) > 0:
                        full_flag = True
                        break
        if full_flag:
            result.append(str(topic["_id"]))

    return result


def filters(db, filter_cfg):
    unit_rule = filter_cfg['rule']
    if unit_rule['type'] == 'course':
        # course filters
        if unit_rule['filter'] == 'payable_course':
            result = payable_course(db)

        # topic options
        if 'options' in unit_rule and len(unit_rule['options']) > 0:
            if 'full_topics' in unit_rule['options'] and unit_rule['options']['full_topics']:
                result['topic_id'] = full_topics(db, result['topic_id'])

    return result
