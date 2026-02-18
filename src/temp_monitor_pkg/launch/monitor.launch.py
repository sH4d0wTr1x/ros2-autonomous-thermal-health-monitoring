"""
LAUNCH FILE
-----------
Instead of running 3 separate terminals, this file starts
ALL THREE nodes with one command:
  ros2 launch temp_monitor_pkg monitor.launch.py
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """ROS2 calls this function to know what to start."""

    return LaunchDescription([

        # Node 1: Temperature Sensor (Publisher)
        Node(
            package='temp_monitor_pkg',
            executable='temp_sensor',
            name='temp_sensor',
            output='screen',           # Show logs in terminal
            emulate_tty=True           # Enable colored output
        ),

        # Node 2: Temperature Monitor (Subscriber + Publisher)
        Node(
            package='temp_monitor_pkg',
            executable='temp_monitor',
            name='temp_monitor',
            output='screen',
            emulate_tty=True
        ),

        # Node 3: Logger (Subscriber)
        Node(
            package='temp_monitor_pkg',
            executable='logger',
            name='logger',
            output='screen',
            emulate_tty=True
        ),

    ])