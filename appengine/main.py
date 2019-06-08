from flask import Flask, request, send_file
from flask_sockets import Sockets
import json
import base64
import os


# THIS IS FOR DEBUGGING ONLY
# NOTE:
# Please comment this out when deploy to the app engine
#TOKEN = "1234abcd"

# PRODUCTION ENV
# NOTE:
# Please uncomment this when deploy to the app engine
TOKEN = os.environ.get("TOKEN")

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
    #payload = base64.b64decode(envelope["message"]["data"]).decode("ascii")
    payload = envelope["message"]["data"]
    print("received a good payload\n")

    if current_ws is not None:
        # loop through the connected clients
        clients = current_ws.handler.server.clients.values()
        for client in clients:
            client.ws.send(payload)
    return "OK\n", 200


@app.route('/')
def index():
    return send_file('index.html')

if __name__ == '__main__':
    print("""
This can not be run directly because the Flask development server does not
support web sockets. Instead, use gunicorn:

gunicorn -b 127.0.0.1:8080 -k flask_sockets.worker main:app

""")
