# c2/app.py
from flask import Flask
from flask_socketio import SocketIO
from db import init_db
from routes import register_routes
from sockets import register_sockets

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-key'
socketio = SocketIO(app, cors_allowed_origins="*")

init_db()
register_routes(app, socketio)
register_sockets(socketio)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001)
