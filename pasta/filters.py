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


def full_topic(course_db, topic_list):
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

# # {
# #     "type": "course.payable",
# #     "apply": {
# #         "numerator.config.eventValue.topicId": {"$in": ">>topic<<"},
# #         "denominator.config.eventValue.topicId": {"$in": ">>topic<<"}
# #     }
# class Filter:
#     type = ""
#     def __init__(self, filter_dict):
#         self.type = filter_dict['type']
#         self.subclass = self.type.split('.')[0]
#
#         if self.subclass == 'course':
#             course = Course()
#             self.result = eval(self.type)
