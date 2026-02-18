"""Thermal Alert Logging and Data Archival Node.

This module implements a data logging service for the distributed thermal
monitoring system. It consumes fault alerts from the state estimator,
maintains an in-memory log with timestamps, and provides periodic summaries
for system diagnostics and post-mission analysis.

Architecture Role:
    Actor (Data Logger) in a Sense-Think-Act distributed autonomous system.

Subscribed Topics:
    /alerts (std_msgs/String): Fault alert messages with reasoning from
        the state estimator node.

Logging Behavior:
    - Timestamp all incoming alerts (HH:MM:SS format)
    - Store in memory for real-time access during mission
    - Print running summary every 5 alerts received
    - In production, would write to persistent storage or telemetry system

Typical Usage:
    ros2 launch temp_monitor_pkg monitor.launch.py
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from datetime import datetime


class Logger(Node):
    """Thermal alert logger and data archival node.

    This node implements the \"Act\" phase of the Sense-Think-Act cycle
    by persisting all system events. It maintains a running log that
    enables post-mission analysis of thermal behavior and fault history.
    """

    def __init__(self):
        super().__init__('logger')

        # Subscribe to alerts
        self.subscription = self.create_subscription(
            String,
            '/alerts',
            self.log_alert,
            10
        )

        # Keep a list of all received alerts in memory
        self.alert_history = []

        self.get_logger().info('📋 Logger Node started! Listening for alerts on /alerts ...')

    def log_alert(self, msg):
        """Archive thermal fault alert to persistent log.

        This callback appends incoming fault alerts to the system log
        with precise timestamps for mission telemetry analysis. Prints
        periodic summaries for real-time operator awareness.

        Args:
            msg (std_msgs/String): Incoming fault alert message from
                the state estimator node.
        """

        # Add timestamp to the alert
        timestamp = datetime.now().strftime('%H:%M:%S')
        entry = f'[{timestamp}] {msg.data}'

        # Store in history
        self.alert_history.append(entry)

        # Print to console
        self.get_logger().warn(f'📝 LOGGED ALERT #{len(self.alert_history)}: {entry}')

        # Every 5 alerts, print a summary
        if len(self.alert_history) % 5 == 0:
            self.get_logger().info('--- ALERT SUMMARY ---')
            for i, alert in enumerate(self.alert_history, 1):
                self.get_logger().info(f'  {i}. {alert}')
            self.get_logger().info(f'--- Total alerts logged: {len(self.alert_history)} ---')


def main(args=None):
    rclpy.init(args=args)
    node = Logger()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()