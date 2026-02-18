# ROS2 Distributed Thermal Monitoring System

A ROS 2 distributed health monitoring application demonstrating the **Sense-Think-Act** cycle in autonomous systems.




![ROS2](https://img.shields.io/badge/ROS2-Humble-blue?logo=ros)
![Python](https://img.shields.io/badge/Python-3.10-g?logo=python)
![Docker](https://img.shields.io/badge/Docker-Compose-informational?logo=docker)
![License](https://img.shields.io/badge/License-Educational-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)


## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Architecture: The Sense-Think-Act Cycle](#architecture-the-sense-think-act-cycle)
- [System Components](#system-components)
- [Project Files & Structure](#project-files--structure)
- [Getting Started](#getting-started)
- [Running the System](#running-the-system)
- [Docker Deployment](#docker-deployment)
- [Testing & Validation](#testing--validation)

---

## 🎯 Project Overview

This project is a **distributed thermal monitoring system** for autonomous platforms. It simulates real-world sensor networks where:

- **Temperature sensors** continuously measure system thermal state (Sense)
- **A monitor node** analyzes readings and makes safety decisions (Think)
- **A logger node** records all events for post-mission analysis (Act)

All three components communicate asynchronously using **ROS 2 topics**, demonstrating how modular, scalable systems handle real-time fault detection on autonomous vehicles.

---

## 🔄 Architecture: The Sense-Think-Act Cycle

The **Sense-Think-Act** cycle is a fundamental pattern in autonomous systems. Here's the demonstration:

### 1. **SENSE** 🌡️ — Temperature Telemetry Acquisition
```
temp_sensor (Publisher)
    ↓
    Acquires thermal readings every 2 seconds
    ↓
    Publishes to /temperature topic (std_msgs/Float32)
```

**What happens:**
- The sensor node simulates a hardware temperature sensor
- Generates realistic readings: 70% normal (18-28°C), 15% warning zone (5-15°C), 15% danger zone (35-45°C)
- Broadcasts readings so other nodes can subscribe

---

### 2. **THINK** 🧠 — State Estimation & Fault Detection
```
temp_monitor (Subscriber + Publisher)
    ↓
    Receives temperature readings from /temperature
    ↓
    Classifies state: OK → WARNING → DANGER
    ↓
    Publishes alerts to /alerts topic (std_msgs/String)
```

**What happens:**
- The monitor node implements a **finite state machine** with three states:
  - **OK** (🟢): 15°C ≤ T ≤ 28°C — Normal operation
  - **WARNING** (🟡): 28°C < T < 35°C or 10°C < T < 15°C — Elevated risk
  - **DANGER** (🔴): T ≥ 35°C or T ≤ 10°C — Critical condition
- Updates running statistics (average temperature, reading count)
- Triggers alerts only when abnormal conditions detected
- This is the "intelligence" of the system

---

### 3. **ACT** 📝 — Data Logging & Response
```
logger (Subscriber)
    ↓
    Receives fault alerts from /alerts
    ↓
    Timestamps each alert and stores in memory
    ↓
    Prints summary every 5 alerts
```

**What happens:**
- The logger node records all system events with precise timestamps
- In production, this would write to:
  - File system for post-flight analysis
  - Cloud telemetry server
  - Onboard database
- Enables post-mission diagnostics: "What went wrong and when?"

---

## 🏗️ System Components

### Node 1: `temp_sensor.py` — The "Sense" Node
**Role:** Publisher of thermal telemetry

| Aspect | Details |
|--------|---------|
| **Type** | ROS 2 Node (Publisher) |
| **Publishes** | `/temperature` (std_msgs/Float32) every 2 seconds |
| **Simulation** | Realistic temperature distribution with anomalies |
| **Purpose** | Continuously feed thermal data to the monitoring network |

**Key Methods:**
- `__init__()`: Creates a publisher and sets up a 2-second timer
- `publish_temperature()`: Called by timer; generates and publishes a reading

---

### Node 2: `temp_monitor.py` — The "Think" Node
**Role:** State estimator and fault detector

| Aspect | Details |
|--------|---------|
| **Type** | ROS 2 Node (Subscriber + Publisher) |
| **Subscribes to** | `/temperature` (Float32 readings) |
| **Publishes to** | `/alerts` (String messages) |
| **State Machine** | 3 discrete states (OK, WARNING, DANGER) |
| **Purpose** | Real-time thermal state classification and fault alerting |

**Key Methods:**
- `__init__()`: Creates subscription to `/temperature` and publisher for `/alerts`
- `analyze_temperature(msg)`: Called for each reading; implements state logic
  1. Receives temperature value
  2. Compares against thresholds
  3. Updates statistics
  4. Publishes alert if abnormal

**Configurable Thresholds:**
```python
TEMP_HIGH_DANGER  = 35.0°C
TEMP_HIGH_WARNING = 28.0°C
TEMP_LOW_WARNING  = 15.0°C
TEMP_LOW_DANGER   = 10.0°C
```

---

### Node 3: `logger.py` — The "Act" Node
**Role:** Data archival and event logging

| Aspect | Details |
|--------|---------|
| **Type** | ROS 2 Node (Subscriber) |
| **Subscribes to** | `/alerts` (Alert messages from monitor) |
| **Storage** | In-memory list with timestamps |
| **Output** | Console summaries + future persistence |
| **Purpose** | Mission telemetry recording for diagnostics |

**Key Methods:**
- `__init__()`: Creates subscription to `/alerts`
- `log_alert(msg)`: Called for each alert; stores with timestamp

---

## 📁 Project Files & Structure

```
ros2_temp_ws/
├── .gitignore                          ← Excludes build/install/venv from Git
├── README.md                           ← This file (project documentation)
├── Dockerfile                          ← Containerizes the ROS 2 environment
├── docker-compose.yml                  ← Orchestrates container startup
│
└── src/temp_monitor_pkg/
    ├── package.xml                     ← ROS 2 package metadata (name, version, dependencies)
    ├── setup.py                        ← Python installer (registers nodes as executables)
    ├── setup.cfg                       ← Build configuration
    │
    ├── temp_monitor_pkg/               ← MAIN SOURCE FOLDER
    │   ├── __init__.py                 ← Makes this a Python package
    │   ├── temp_sensor.py              ← Sensor node (SENSE phase)
    │   ├── temp_monitor.py             ← Monitor node (THINK phase)
    │   └── logger.py                   ← Logger node (ACT phase)
    │
    ├── launch/
    │   └── monitor.launch.py           ← Starts all 3 nodes simultaneously
    │
    ├── msg/
    │   └── TempAlert.msg               ← Custom message type (for extensibility)
    │
    └── test/
        ├── test_copyright.py           ← Checks copyright headers
        ├── test_flake8.py              ← Python style checker
        └── test_pep257.py              ← Docstring checker
```

### What Each File Does

| File | Purpose |
|------|---------|
| `.gitignore` | Prevents Git from tracking build artifacts, Python cache, and Docker files |
| `package.xml` | ROS 2 package metadata (name: `temp_monitor_pkg`, dependencies: `rclpy`, `std_msgs`) |
| `setup.py` | Registers node executables so ROS 2 can find and run them |
| `setup.cfg` | Python package build settings |
| `temp_sensor.py` | Simulates hardware sensor; publishes `/temperature` topic |
| `temp_monitor.py` | Analyzes readings and publishes `/alerts` when out-of-range |
| `logger.py` | Subscribes to `/alerts`; stores events with timestamps |
| `monitor.launch.py` | Launch file that starts all 3 nodes with one command |
| `Dockerfile` | Sets up Ubuntu + ROS 2 + builds the package inside a container |
| `docker-compose.yml` | Orchestration file; simplifies Docker startup with one command |

---

## 🚀 Getting Started

### Prerequisites

- **Ubuntu 20.04 or 22.04** (or use Docker)
- **ROS 2 Humble** installed ([Installation Guide](https://docs.ros.org/en/humble/Installation.html))
- **Python 3.8+**
- **Git** (for version control)

---

## 📚 Essential Linux Commands Reference

Before diving into the ROS 2 setup, here are the basic Linux commands you'll use:

| Command | Purpose | Example |
|---------|---------|---------|
| `pwd` | Print current directory path | `pwd` → `/home/shariq/ros2_temp_ws` |
| `cd` | Change directory | `cd ~/ros2_temp_ws` |
| `ls` | List directory contents | `ls -la` (detailed view) |
| `mkdir` | Create a new directory | `mkdir -p ~/ros2_temp_ws/src` |
| `touch` | Create empty file or update timestamp | `touch Dockerfile` |
| `cat` | Display file contents | `cat README.md` |
| `echo` | Print text or create file with content | `echo "Hello" > file.txt` |
| `cp` | Copy files or directories | `cp file.txt file_copy.txt` |
| `mv` | Move or rename files | `mv oldname.py newname.py` |
| `rm` | Remove files (⚠️ be careful!) | `rm file.txt` |
| `gedit` or `nano` | Text editor | `nano setup.py` |
| `sudo` | Run with administrator privileges | `sudo apt update` |
| `apt` | Ubuntu package manager | `sudo apt install python3` |

### Navigation Examples

```bash
# Navigate to home directory
cd ~

# Navigate to workspace root
cd ~/ros2_temp_ws

# Navigate back one directory
cd ..

# Navigate to specific folder
cd src/temp_monitor_pkg

# Create nested directories at once
mkdir -p ~/ros2_temp_ws/src/temp_monitor_pkg/launch

# See where you are
pwd

# List all files with details
ls -la

# List files recursively
ls -R
```

### File Operations Examples

```bash
# Create empty files
touch file1.py file2.py file3.py

# View file contents
cat setup.py

# Copy a file
cp setup.py setup.py.backup

# Move/rename a file
mv oldname.txt newname.txt

# Delete a file (careful!)
rm temporary_file.txt

# Create file with content using echo
echo "#!/usr/bin/env python3" > script.py
```

---

### Step 1: Clone or Navigate to the Workspace

```bash
cd ~/ros2_temp_ws
```

### Step 2: Install Dependencies

```bash
# Install Python dependencies (if any)
# This project uses only standard ROS 2 packages: rclpy, std_msgs

# Verify ROS 2 is sourced
source /opt/ros/humble/setup.bash
```

### Step 3: Build the Package

```bash
# Navigate to workspace root
cd ~/ros2_temp_ws

# Build all packages
colcon build

# You should see:
# Summary: 1 package finished [X.XXs]
```

### Step 4: Source the Build

```bash
# Tell your terminal about the newly built package
source install/setup.bash
```

---

## ▶️ Running the System

### Option 1: Standard ROS 2 Launch (Local)

```bash
# From workspace root
cd ~/ros2_temp_ws
source install/setup.bash

# Start all three nodes together
ros2 launch temp_monitor_pkg monitor.launch.py
```

**Expected Output:**
```
[temp_sensor]:   🌡️  Temp Sensor Node started! Publishing to /temperature every 2s
[temp_monitor]:  🔍 Temp Monitor Node started!
[logger]:        📋 Logger Node started! Listening for alerts on /alerts ...

[temp_sensor]:   📤 Published temperature: 22.3°C
[temp_monitor]:  🟢 Reading #1: 22.3°C | Status: OK | Avg so far: 22.3°C

[temp_sensor]:   📤 Published temperature: 38.7°C
[temp_monitor]:  🔴 Reading #2: 38.7°C | Status: DANGER | Avg so far: 30.5°C
[temp_monitor]:  🚨 Alert published: [DANGER] Temperature too HIGH (38.7°C >= 35.0°C) | Reading #2
[logger]:        📝 LOGGED ALERT #1: [14:32:05] [DANGER] Temperature too HIGH...
```

### Option 2: Run Nodes Individually (Advanced)

If you want to start each node in a separate terminal:

**Terminal 1 - Sensor:**
```bash
source install/setup.bash
ros2 run temp_monitor_pkg temp_sensor
```

**Terminal 2 - Monitor:**
```bash
source install/setup.bash
ros2 run temp_monitor_pkg temp_monitor
```

**Terminal 3 - Logger:**
```bash
source install/setup.bash
ros2 run temp_monitor_pkg logger
```

### Monitoring Tools: "Spy" on the System

While the nodes are running, open a **new terminal tab** and run:

```bash
source /opt/ros/humble/setup.bash

# See all active topics
ros2 topic list
# Expected: /temperature, /alerts, /parameter_events, /rosout

# Watch temperature values live (in real-time)
ros2 topic echo /temperature

# Watch alerts live
ros2 topic echo /alerts

# See all running nodes
ros2 node list
# Expected: /temp_sensor, /temp_monitor, /logger

# See who's talking on each channel
ros2 topic info /temperature
# Expected: Publisher: 1 (temp_sensor)
#           Subscription: 1 (temp_monitor)
```

---

## 🐳 Docker Deployment

Docker packages your entire ROS 2 environment into a container, ensuring it runs identically on any machine.

### Step 1: Build the Docker Image

```bash
cd ~/ros2_temp_ws

# Build the image (first time takes ~2-3 minutes)
docker compose build
```

### Step 2: Run with Docker Compose

```bash
# Start the entire system inside Docker
docker compose up
```

You'll see the same output as before, but now running inside a container.

### Step 3: Stopping Docker

```bash
# In the terminal running docker compose up, press: Ctrl + C

# Or in another terminal
docker compose down
```

### Docker Commands Reference

| Command | Purpose |
|---------|---------|
| `docker compose build` | Build the image (do after code changes) |
| `docker compose up` | Start the system |
| `docker compose down` | Stop and clean up |
| `docker exec -it temp_monitor_system bash` | Open a shell inside the running container |

---

## 🧪 Testing & Validation

### Verify the System is Working

While `ros2 launch` is running in one terminal:

**Test 1: Check Topics Exist**
```bash
ros2 topic list
# Should show: /temperature, /alerts
```

**Test 2: Watch Temperature Data**
```bash
ros2 topic echo /temperature --once
# Output: data: 22.5
```

**Test 3: Trigger an Alert Manually**
```bash
# Run a script in another terminal to publish a dangerous temperature
ros2 topic pub /temperature std_msgs/Float32 '{data: 40.0}'
# Should trigger: [DANGER] alert in temp_monitor
```

**Test 4: Check Alert Messages**
```bash
ros2 topic echo /alerts --once
# Output: data: '[DANGER] Temperature too HIGH...'
```

---
### Key Concepts Demonstrated

| Concept | Implementation |
|---------|-----------------|
| **Distributed Systems** | 3 independent nodes communicating via async messaging |
| **Real-time Processing** | Sensors publish every 2 seconds; monitor reacts immediately |
| **Fault Detection** | Threshold-based anomaly detection with state machine |
| **Telemetry & Logging** | Persistent event recording for post-mission analysis |
| **System Architecture** | Sense-Think-Act cycle for autonomous platforms |
| **DevOps & Containerization** | Docker + Docker Compose for reproducible deployment |

### Autonomous Systems Principles

The Sense-Think-Act pattern mirrors real autonomous systems:
- **Unmanned Aerial Vehicles (UAVs)**: Sense camera/lidar → Think path planning → Act motor control
- **Autonomous Vehicles**: Sense radar/camera → Think behavior planning → Act steering/acceleration
- **Robotic Arms**: Sense joint encoders → Think inverse kinematics → Act joint motors

This thermal monitor is a simplified but architecturally-sound example.

---

## 🔧 Troubleshooting

### Issue: "ros2 command not found"
**Solution:** You haven't sourced ROS 2 setup. Run:
```bash
source /opt/ros/humble/setup.bash
```

### Issue: "Can't find package temp_monitor_pkg"
**Solution:** You haven't built or sourced the workspace. Run:
```bash
cd ~/ros2_temp_ws
colcon build
source install/setup.bash
```

### Issue: "Port already in use" (Docker)
**Solution:**
```bash
docker compose down  # Stop existing containers
docker compose up    # Restart fresh
```

### Issue: No messages appearing in logs
**Solution:** Verify nodes started correctly:
```bash
ros2 node list    # Should show 3 nodes
ros2 topic list   # Should show /temperature, /alerts
```

---

## 📖 Additional Resources

- **ROS 2 Documentation**: https://docs.ros.org/
- **colcon Build System**: https://colcon.readthedocs.io/
- **Docker Documentation**: https://docs.docker.com/
- **Python Style Guide (PEP 8)**: https://pep8.org/

---

## 💡 Future Enhancements

Potential improvements for production deployment:

- [ ] Add persistent database logging (SQLite, PostgreSQL)
- [ ] Implement predictive maintenance using ML models
- [ ] Add REST API for external monitoring
- [ ] Publish metrics to Prometheus/Grafana
- [ ] Add hardware support (actual I2C/SPI temperature sensors)
- [ ] Implement redundancy (multiple sensors per channel)
- [ ] Add CI/CD pipeline (GitHub Actions)

---

## �️ Complete Step-by-Step Deployment Guide

### Phase 1: Workspace & Package Creation

Start from scratch or replicate the entire project:

```bash
# 1. Create the workspace and source folders
mkdir -p ~/ros2_temp_ws/src
cd ~/ros2_temp_ws/src

# 2. Initialize Git (optional)
git init

# 3. Create the Python package
ros2 pkg create --build-type ament_python temp_monitor_pkg --dependencies rclpy std_msgs

# 4. Create the launch and message folders
mkdir -p temp_monitor_pkg/launch
mkdir -p temp_monitor_pkg/msg
```

### Phase 2: Create Empty Files (Project Structure)

```bash
# 5. Navigate to workspace root
cd ~/ros2_temp_ws

# 6. Create Docker files
touch Dockerfile docker-compose.yml

# 7. Create message and launch files
touch src/temp_monitor_pkg/msg/TempAlert.msg
touch src/temp_monitor_pkg/launch/monitor.launch.py

# 8. Create Python node files (in INNER package folder)
touch src/temp_monitor_pkg/temp_monitor_pkg/temp_sensor.py
touch src/temp_monitor_pkg/temp_monitor_pkg/temp_monitor.py
touch src/temp_monitor_pkg/temp_monitor_pkg/logger.py

# 9. Verify your workspace structure
cd ~/ros2_temp_ws
ls -R
```

### Phase 3: Add Content to Files

In order, populate these files:
1. `src/temp_monitor_pkg/package.xml` — Define dependencies
2. `src/temp_monitor_pkg/setup.py` — Register nodes as executables
3. `src/temp_monitor_pkg/setup.cfg` — Build configuration
4. `src/temp_monitor_pkg/temp_monitor_pkg/temp_sensor.py` — Sensor node logic
5. `src/temp_monitor_pkg/temp_monitor_pkg/temp_monitor.py` — Monitor node logic
6. `src/temp_monitor_pkg/temp_monitor_pkg/logger.py` — Logger node logic
7. `src/temp_monitor_pkg/launch/monitor.launch.py` — Launch script
8. `Dockerfile` — Container setup
9. `docker-compose.yml` — Orchestration
10. `.gitignore` — Version control exclusions

### Phase 4: Build & Run Locally

```bash
# 10. Navigate to workspace root
cd ~/ros2_temp_ws

# 11. Build the package
colcon build
# Expected output: Summary: 1 package finished [X.XXs]

# 12. Source the installation
source install/setup.bash

# 13. Run the system
ros2 launch temp_monitor_pkg monitor.launch.py
```

---

## 📋 The Correct Order of Operations

This is the **daily development cycle** you will follow:

### Edit Phase
1. **package.xml** — Define dependencies (e.g., `std_msgs`, `rclpy`)
2. **setup.py** — Register nodes under `console_scripts` so ROS 2 can find them
3. **Node Files** — Write logic in `temp_sensor.py`, `temp_monitor.py`, `logger.py`
4. **Launch File** — Create `monitor.launch.py` to group nodes together

### Build & Deploy Phase
5. **colcon build** — MUST run after editing setup.py or adding new files
6. **source install/setup.bash** — Tell terminal about the fresh build
7. **ros2 launch ...** — Start the system

---

## ❓ ros2 launch vs ros2 run

### ros2 run
- Runs a **single node** in isolation
- You would need **3 separate terminals** for your 3-node system
- Command: `ros2 run temp_monitor_pkg temp_sensor`

### ros2 launch
- Runs a **launch file** that can start multiple nodes
- Manages all nodes with **one command**
- Can orchestrate 10, 100, or 1000s of nodes simultaneously
- Command: `ros2 launch temp_monitor_pkg monitor.launch.py`

**In your project:** Use `ros2 launch` because you want sensor, monitor, and logger to start together as one integrated system.

---

## 🐳 Docker Deployment & Integration

### Why Docker?

Ensures your ROS 2 environment runs identically on any machine:
- Local Ubuntu: Exactly the same output
- CI/CD pipeline: Same behavior
- Colleague's laptop: No "works on my machine" problems

### Dockerfile vs Docker Compose

#### Dockerfile
- **Purpose:** Builds a container image
- **Contains:** OS, ROS 2, dependencies, your code, build artifacts
- **Command:** `docker build` (rarely used directly in this project)

#### Docker Compose
- **Purpose:** Orchestrates container startup with rules
- **Advantage:** Saves typing long docker commands repeatedly
- **Example:** Without Compose, you'd type:
  ```bash
  docker run -it --network host --name temp_system temp_monitor_image
  ```
  With Compose, just:
  ```bash
  docker compose up
  ```

### Network Configuration

Your `docker-compose.yml` includes `network_mode: host`:
- **Without this:** Container is isolated; can't see host topics
- **With this:** Container nodes can communicate with Ubuntu terminal monitoring

### Docker Container Architecture

**Option 1 (Recommended):**
- Single container runs all 3 nodes (sensor, monitor, logger)
- Simpler deployment, faster startup

**Option 2 (Advanced):**
- Separate containers for each node
- Allows independent scaling (use if one node bottlenecks)

---

## 🐳 Docker Command Reference

### First-Time Setup

```bash
cd ~/ros2_temp_ws

# Build the image (takes 2-3 minutes initially)
docker compose build

# Start the system
docker compose up
```

### Common Scenarios

| Scenario | Command |
|----------|---------|
| First time running | `docker compose up --build` |
| After editing Python code | `docker compose build && docker compose up` |
| Quick restart (images exist) | `docker compose up` |
| Stop completely | `docker compose down` |
| Explore inside container | `docker exec -it temp_monitor_system bash` |

### Individual Docker Commands

```bash
# Run one node manually in Docker
docker run -it temp_monitor_system ros2 run temp_monitor_pkg temp_sensor

# Open shell inside running container
docker exec -it temp_monitor_system bash
# Inside, you can run:
#   ros2 node list
#   ros2 topic list
#   ros2 topic echo /temperature

# View logs from container
docker logs temp_monitor_system

# Remove old containers
docker system prune

# Stop running container
docker compose down
```

### Stopping & Cleanup

```bash
# Option 1: Press Ctrl+C in the terminal running docker compose up

# Option 2: In another terminal
docker compose down

# Option 3: Full cleanup (removes images, volumes)
docker compose down -v
```

---

## 🔄 Development Checklist

Use this checklist for any changes to your project:

- [ ] **Code:** Edit files (nodes, launch, config)
- [ ] **Build:** Run `colcon build`
- [ ] **Source:** Run `source install/setup.bash`
- [ ] **Test:** Run `ros2 launch temp_monitor_pkg monitor.launch.py`
- [ ] **Verify:** Check `ros2 topic list` and `ros2 node list`
- [ ] **Commit:** `git add . && git commit -m "message"`

---

## �📝 License & Attribution

Built as an educational project for my studies. This repository demonstrates distributed systems architecture in ROS 2.

---

**Framework:** ROS 2 Humble  
**Language:** Python 3.10