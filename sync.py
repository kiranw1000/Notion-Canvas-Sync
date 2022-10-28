from canvasapi import Canvas, assignment
import canvasapi as cnv
from tokens import canvas_token, notion_token
from notion_client import Client
from datetime import datetime,timedelta
import pytz

nclient = Client(auth=notion_token)
API_URL = "https://osu.instructure.com/"
API_KEY = canvas_token
canvas = Canvas(API_URL,API_KEY)
kiran = canvas.get_current_user()
courses = [x for x in kiran.get_courses()]
db_id = "57c6c1fdb5b54861af2fb7787344b4fc"
subjects = {
     'AU22 CSE 2221 - SW 1: Components (35445)':{'id': '8d669188-3c5e-4fea-84e4-2cb3fcf74ca8','name': 'Software Engineering 2221','color': 'yellow'},
     'AU22 ENGR 1181.01 - Fund Engr 1 (7063)':{'id': '9ff6a39b-c700-4ab7-9d66-29d963f01e8f','name': 'Intro to Engineering','color': 'green'},
     'AU22 ARTSSCI 1100.01H - ASC College Survey (15218)':{'id': 'e18cd657-84af-4152-a783-be92991ca93b','name': 'Art Sci Survey','color': 'default'},
     'AU22 PHYSICS 1250H - Mechanics, Spc Rel (20281)':{'id': '6dcb6cd3-3d2c-46d5-a070-f6f8bdb6969c','name': 'Physics 1250H','color': 'purple'},
     'AU22 MATH 2153 - Calculus 3 (18401)':{'id': '85591cad-2e1b-44f7-b06f-05f45a081c95','name': 'Calc 2153','color': 'red'}}

def get_schema(assignment:assignment,subject_dict:dict,course:str):
    backlog = {'id': '1', 'name': 'Backlog', 'color': 'red'}
    week_backlog = {'id': '2', 'name': 'Week Backlog', 'color': 'yellow'} 
    status = ""
    if assignment.due_at_date.date()-datetime.today().date()<=timedelta(days=7):
        status = week_backlog
    else:
        status = backlog
    schema = {
    "Status":{"select": status},
    'Name': {"title": [{"type":"text","text":{"content":assignment.name}}]},
    "Subject":{"select":subject_dict[course]},
    "Due Date":{"date":{"start":datetime.strptime(assignment.due_at,"%Y-%m-%dT%H:%M:%S%z").astimezone(pytz.timezone('US/Eastern')).strftime("%Y-%m-%dT%H:%M:%S%z")}},
    "Link":{"url":assignment.html_url},
    "Time to complete":{"select":{'id': 'b261419e-254f-44b9-8788-1532a54646fb','name': 'About an hour','color': 'red'}}
    }
    return schema

def add_assignment(assignment:assignment,subject_dict:dict,course:str):
    return nclient.pages.create(**{"parent":{"type":"database_id","database_id":db_id},"properties":get_schema(assignment,subjects,course)})


def update_course(course:cnv.course.Course,subject_dict:dict):
    course_assignments = [y for y in kiran.get_assignments(course)]
    for x in course_assignments:
        if len(nclient.databases.query(**{"database_id":db_id,"filter":{"property":"Name","title":{"contains":x.name}}})['results'])<1 and x.get_submission(kiran).submitted_at==None and x.due_at!=None:
            print(x)
            print(add_assignment(assignment=x,subject_dict=subject_dict,course=course.name)['properties']['Name'])

def update_all(courses:list,subject_dict:dict):
    backlog = {'id': '1', 'name': 'Backlog', 'color': 'red'}
    week_backlog = {'id': '2', 'name': 'Week Backlog', 'color': 'yellow'} 
    backloglist = nclient.databases.query(**{"database_id":db_id,"filter":{"property":"Status","select":{"equals":"Backlog"}}})['results']
    for page in backloglist:
        date = datetime.fromisoformat(page['properties']['Due Date']['date']['start'])
        if date.date()-datetime.today().date()<timedelta(days=7):
            nclient.pages.update(page['id'],**{'properties':{'Status':{'select':week_backlog}}})
    for x in courses:
        update_course(x,subject_dict)

update_all(courses=courses,subject_dict=subjects)


