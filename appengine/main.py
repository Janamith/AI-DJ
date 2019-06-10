from flask import Flask, request, send_file
from flask_sockets import Sockets
import json
import base64
import os
from datetime import datetime
import sqlalchemy

# THIS IS FOR DEBUGGING ONLY
# NOTE:
# Please comment this out when deploy to the app engine
CONNECTION_NAME = "bigdata"       # "YOUR_DB_INSTANCE_NAME"
DB_USER = "postgres"              # "YOUR_DB_USERNAME"   # usually postgres
DB_PASSWORD = "HnusABOqiqMGfL00"  # "YOUR_DB_PASSWORD"
DB_NAME = "postgres"              # usually postgres
TOKEN = "1234abcd"                # can be anything unique

# PRODUCTION ENV
# NOTE:
# Please uncomment this when deploy to the app engine
#   CONNECTION_NAME = os.environ.get("CONNECTION_NAME")
#   DB_USER = os.environ.get("DB_USER")
#   DB_PASSWORD = os.environ.get("DB_PASSWORD")
#   DB_NAME = os.environ.get("DB_NAME")
#   TOKEN = os.environ.get("TOKEN")

# set up database
db = sqlalchemy.create_engine(
    # Equivalent URL:
    # postgres+psycopg2://<db_user>:<db_pass>@/<db_name>?unix_socket=/cloudsql/<cloud_sql_instance_name>
    sqlalchemy.engine.url.URL(
        drivername='postgres+psycopg2',
        username=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        # comment the line below if you want to use local sql proxy
        host='/cloudsql/{}'.format(CONNECTION_NAME)
        # uncomment these two lines below to enable local sql proxy connection
        # you may need to change the port number based on your
        # local sql proxy setup
        # host="localhost",
        # port=3306
    ),
)

# setup flask
app = Flask(__name__)
sockets = Sockets(app)
current_ws = None

def request_arg(request_args, request_json, arg_name):
    if request_json:
        return request_json[arg_name]
    else:
        return request_args[arg_name]

@sockets.route('/emotion')
def image_socket(ws):
    global current_ws
    token = request.args.get("token", "")
    if token != TOKEN:
        return "Unknown token", 401
    current_ws = ws
    while not ws.closed:
        message = ws.receive()
        if message is None:  # message is "None" if the client has closed.
            continue


@app.route("/emotion-push", methods=["POST"])
def pubsub_push():
    if request.args.get("token", "") != TOKEN:
        return "Invalid request", 400
    envelope = json.loads(request.data.decode("utf-8"))
    message = envelope["message"]
    print("received message:", message)

    # decode message: emotion, deviceid, and time
    emotions = message["emotions"]
    #payload = base64.b64decode(message["data"]).decode("ascii")
    device_id = message["device_id"]
    time = message["published_at"]
    #current_time = datetime.strptime(time_raw, '%Y-%m-%dT%H:%M:%S.%fZ')
    #timestamp = int((current_time - datetime(1970, 1, 1)).total_seconds())

    #with db.connect() as conn:
    #    for emotion in emotions:
    #        print("inserting",emotion,"into the database (jk not yet)")
    #        sql_cmd = sqlalchemy.text("INSERT INTO emotions (time, emotion, device_id) values (:time, :emotion, :device_id)")
    #        conn.execute(sql_cmd, {"time":str(timestamp), "emotion":str(emotion), "device_id":str(device_id)})

    #if current_ws is not None:
    #    # loop through the connected clients
    #    clients = current_ws.handler.server.clients.values()
    #    for client in clients:
    #        client.ws.send(payload)

    
    return "OK\n", 200


@app.route('/')
def index():
    # get the current system time and use to construct time range for data selection
    #start_time = request.args.get("start_time", "")
    #end_time = request.args.get("end_time", "")

    emotions = []
    with db.connect() as conn:
        sql_cmd = sqlalchemy.text("SELECT * FROM emotions WHERE time BETWEEN :start AND :end")
        sql_lines = conn.execute(sql_cmd, {"start":start_time, "end":end_time})
        fetched_lines = sql_lines.fetchall()
        print(fetched_lines)
        for kv in fetched_lines:
            emotions.append({"time": kv[0], "emotion": kv[1], "device_id": kv[2]})

    dominant_emotion = max(emotion, key=emotion.count)
    #change_music(dominant_emotion, previous_emotion)
    print("dominant emotion:", dominant_emotion)

    return send_file('index.html')

if __name__ == '__main__':
    print("""
This can not be run directly because the Flask development server does not
support web sockets. Instead, use gunicorn:

gunicorn -b 127.0.0.1:8080 -k flask_sockets.worker main:app

""")
