# c2/sockets.py
def register_sockets(socketio):
    @socketio.on("connect")
    def handle_connect():
        print("[*] Web client connected")

    @socketio.on("agent_result")
    def handle_agent_result(data):
        socketio.emit("new_result", data)

    @socketio.on("disconnect")
    def handle_disconnect():
        print("[*] Web client disconnected")
