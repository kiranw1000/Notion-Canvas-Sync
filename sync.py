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
courses = []
db_id = "57c6c1fdb5b54861af2fb7787344b4fc"
subjects = {}
enrollment_term_id = 164
for course in kiran.get_courses():
    if course.__dict__['enrollment_term_id'] == enrollment_term_id:
        courses.append(course)

def get_schema(assignment:assignment,subject_dict:dict,course:str):
    backlog = {'id': '1', 'name': 'Backlog', 'color': 'red'}
    week_backlog = {'id': '2', 'name': 'Week Backlog', 'color': 'yellow'} 
    status = ""
    if assignment.due_at_date.date()-datetime.today().date()<=timedelta(days=7):
        status = week_backlog
    else:
        status = backlog
    if course in subject_dict.keys():
        subject = subject_dict[course]
    else:
        subject = {'name':course}
    schema = {
    "Status":{"select": status},
    'Name': {"title": [{"type":"text","text":{"content":assignment.name}}]},
    "Subject":{"select":subject},
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
            add_assignment(assignment=x,subject_dict=subject_dict,course=course.name)['properties']['Name']

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


