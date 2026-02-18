# ─────────────────────────────────────────────────────────────────
# Start from the official ROS2 Humble base image (Ubuntu 22.04)
# This gives us ROS2 already installed — no manual setup needed
# ─────────────────────────────────────────────────────────────────
FROM ros:humble

# Set a working directory inside the container
WORKDIR /ros2_temp_ws

# ─────────────────────────────────────────────────────────────────
# Install dependencies
# ─────────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    ros-humble-launch-ros \
    && rm -rf /var/lib/apt/lists/*

# ─────────────────────────────────────────────────────────────────
# Copy your ROS2 workspace source code into the container
# ─────────────────────────────────────────────────────────────────
COPY src/ /ros2_temp_ws/src/

# ─────────────────────────────────────────────────────────────────
# Build the ROS2 package inside the container
# We use bash -c because we need to source ROS2 first
# ─────────────────────────────────────────────────────────────────
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && \
    cd /ros2_temp_ws && \
    colcon build --symlink-install"

# ─────────────────────────────────────────────────────────────────
# Create an entrypoint script that sources everything automatically
# so you don't have to do it manually inside the container
# ─────────────────────────────────────────────────────────────────
RUN echo '#!/bin/bash\n\
source /opt/ros/humble/setup.bash\n\
source /ros2_temp_ws/install/setup.bash\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Default command: launch all three nodes
CMD ["ros2", "launch", "temp_monitor_pkg", "monitor.launch.py"]