# Notion-Canvas-Sync
Reads assignments from Canvas and adds them to a kanban board in my personal Notion but can be adapted to your own board.<br>

# Setup

Place a page in the location on the board that you want the items to be populated in and name it Marker.<br>
Then, create file called tokens.py in the same directory as this module and fill it in as below:<br>

Get the database id for your database by navigating to it and then getting the id between the / and ? (in the below image it would be 57c6c1fdb5b54861af2fb7787344b4fc) and use it as $db_id below.<br>
![Alt text](image.png)<br>

db_id = $db_id<br>
canvas_token = $canvas_token<br>
notion_token = $notion_token<br>
API_URL = "https://your_school.instructure.com/"<br>

Also, make sure the database you are adding to has the following properties:<br>
Status of type status<br>
Name of type title<br>
Subject of type select<br>
Due Date of type date<br>
Link of type URL<br>

Finally, go into the sync.py function and change the kiran_custom to False unless you are sure you understand what update_all does.<br>

