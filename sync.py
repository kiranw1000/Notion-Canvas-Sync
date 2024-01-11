from canvasapi import Canvas, assignment
import canvasapi as cnv
from tokens import *
from notion_client import Client
from datetime import datetime,timedelta
import pytz

nclient = Client(auth=notion_token)
API_KEY = canvas_token
canvas = Canvas(API_URL,API_KEY)
cnvclient = canvas.get_current_user()
courses = []
subjects = {}
enrollment_term_id = 164
kiran_custom = True

marker = nclient.databases.query(**{"database_id":db_id,"filter":{"property":"Name","title":{"equals":"Marker"}}})['results'][0]

for course in cnvclient.get_favorite_courses():
    if course.__dict__['enrollment_term_id'] == enrollment_term_id:
        courses.append(course)

def get_schema(assignment:assignment,subject_dict:dict,course:str):
    if course in subject_dict.keys():
        subject = subject_dict[course]
    else:
        subject = {'name':course}
    schema = marker["properties"]
    schema.update({
    'Name': {"title": [{"type":"text","text":{"content":assignment.name}}]},
    "Subject":{"select":subject},
    "Due Date":{"date":{"start":datetime.strptime(assignment.due_at,"%Y-%m-%dT%H:%M:%S%z").astimezone(pytz.timezone('US/Eastern')).strftime("%Y-%m-%dT%H:%M:%S%z")}},
    "Link":{"url":assignment.html_url},
    })
    return schema

def add_assignment(assignment:assignment,course:str):
    return nclient.pages.create(**{"parent":{"type":"database_id","database_id":db_id},"properties":get_schema(assignment,subjects,course)})


def update_course(course:cnv.course.Course, verbose=False): 
    course_assignments = [y for y in cnvclient.get_assignments(course)]
    for x in course_assignments:
        if len(nclient.databases.query(**{"database_id":db_id,"filter":{"and":[{"property":"Name","title":{"contains":x.name}},{"property":"Subject","select":{"equals":course.name}}]}})['results'])<1 and x.due_at!=None:
            if verbose : print(x)
            add_assignment(assignment=x,course=course.name)['properties']['Name']

def update_all(courses:list):
    backlog = "Backlog"
    week_backlog = "Week Backlog"
    backloglist = nclient.databases.query(**{"database_id":db_id,"filter":{"property":"Status","status":{"equals":"Backlog"}},"sorts":[{"property":"Due Date","direction":"ascending"}]})['results']
    weekbackloglist = nclient.databases.query(**{"database_id":db_id,"filter":{"property":"Status","status":{"equals":"Week Backlog"}},"sorts":[{"property":"Due Date","direction":"ascending"}]})['results']
    for x in courses:
        update_course(x)
    for page in backloglist:
        date = datetime.fromisoformat(page['properties']['Due Date']['date']['start'])
        if date.date()-datetime.today().date()<=timedelta(days=7):
            nclient.pages.update(page['id'],**{'properties':{'Status':{'status':{'name':week_backlog}}}})
    for page in weekbackloglist:
        if page['properties']['Due Date']['date']!=None:
            date = datetime.fromisoformat(page['properties']['Due Date']['date']['start'])
            if date.date()-datetime.today().date()>timedelta(days=7):
                nclient.pages.update(page['id'],**{'properties':{'Status':{'status':{'name':backlog}}}})

if __name__ == "__main__":
    if kiran_custom:
        update_all(courses=courses)
    else:
        for x in courses:
            update_course(course)


