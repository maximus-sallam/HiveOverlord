# HiveOverlord

**HiveOverlord** is an advanced Command and Control (C2) framework designed to streamline the management and coordination of multiple agents within a network. 
It facilitates centralized tasking, real-time communication, and efficient control over distributed systems, enhancing operational oversight and effectiveness.

## Features

- **Agent Registration:** Agents can register with the HiveOverlord server upon initialization, providing their hostname and tags for identification.
- **Tasking System:** The server can assign tasks to registered agents, which execute the commands and return the results.
- **Persistent Agent ID:** Each agent maintains a unique identifier to ensure consistent communication with the server.
- **Automatic Re-registration:** Agents detect if they have been deregistered (e.g., after server data clearance) and automatically re-register to maintain connectivity.

## Installation

### Server Setup

1. **Clone the Repository:**
```
$ git clone https://github.com/maximus-sallam/HiveOverlord.git
```

2. **Navigate to the Project Directory:**
```
$ cd HiveOverlord
```

3. **Install Dependencies:**
```
$ pip3 install -r requirements.txt
```

4. **Run the Server:**
```
$ python3 app.py
```

## Deploying the zombie.py Agent on a Target System

1. **Transfer the Agent Script**

Option A: Via Secure Copy (SCP)
```
$ scp path/to/zombie.py user@target_system:/desired/path/
```

Option B: Via USB Drive
Copy zombie.py manually to the target system using a USB drive.

2. **Install Required Dependencies**

Ensure Python 3 is installed:
```
$ python3 --version
```

If not installed, refer to the target system's OS-specific instructions to install Python 3.

Install 'requests' library (required for HTTP communication):
```
$ pip3 install requests
```

3. **Configure the Agent Script**

Open zombie.py and update the C2 server URL:
Edit this line:
C2_URL = "http://127.0.0.1:5001"
To match your HiveOverlord server's address and port, for example:
C2_URL = "http://192.168.1.100:5001"

4. **Execute the Agent Script**

On the target system, navigate to the zombie.py directory:
```
$ cd /path/to/zombie.py
```

Then run the agent:
```
$ python3 zombie.py
```

Upon execution, the agent will:
- Register with the HiveOverlord server
- Begin polling for new tasks every 5 seconds
- Execute received tasks and report results

Note:
Make sure the network and firewall settings allow outbound access from the agent
to the HiveOverlord server's IP address and port (default: 5001).
