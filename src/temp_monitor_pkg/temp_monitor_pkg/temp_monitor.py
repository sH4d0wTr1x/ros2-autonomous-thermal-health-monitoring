"""Thermal State Estimation and Anomaly Detection Node.

This module implements a state estimation and fault detection engine
for a distributed thermal monitoring system. It consumes temperature
telemetry from sensor nodes, performs real-time state classification
(OK, WARNING, DANGER), and publishes alerts for detected thermal faults.

Architecture Role:
    Thinker (State Estimator & Fault Detector) in a Sense-Think-Act
    distributed autonomous system.

Subscribed Topics:
    /temperature (std_msgs/Float32): Raw thermal telemetry in Celsius.

Published Topics:
    /alerts (std_msgs/String): Fault alerts with timestamp and reasoning.
        Triggered when system transitions to WARNING or DANGER states.

State Thresholds (configurable parameters):
    DANGER: T >= 35.0°C or T <= 10.0°C
    WARNING: 28.0°C <= T < 35.0°C or 10.0°C < T <= 15.0°C
    OK: 15.0°C < T < 28.0°C

Typical Usage:
    ros2 launch temp_monitor_pkg monitor.launch.py
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String


TEMP_HIGH_DANGER = 35.0
"""float: High temperature danger threshold (Celsius)."""

TEMP_HIGH_WARNING = 28.0
"""float: High temperature warning threshold (Celsius)."""

TEMP_LOW_WARNING = 15.0
"""float: Low temperature warning threshold (Celsius)."""

TEMP_LOW_DANGER = 10.0
"""float: Low temperature danger threshold (Celsius)."""


class TempMonitor(Node):
    """Thermal state estimator and anomaly detector.

    This node implements a finite state machine that classifies incoming
    thermal telemetry into discrete states (OK, WARNING, DANGER) and
    triggers alerts when safety thresholds are exceeded. It maintains
    running statistics for system diagnostics.
    """

    def __init__(self):
        super().__init__('temp_monitor')

        # --- SUBSCRIBE to temperature data ---
        # When a message arrives on /temperature, call self.analyze_temperature
        self.subscription = self.create_subscription(
            Float32,                    # Message type
            '/temperature',             # Topic to listen to
            self.analyze_temperature,   # Callback function
            10                          # Queue size
        )

        # --- PUBLISH alerts ---
        self.alert_publisher = self.create_publisher(String, '/alerts', 10)

        # Track reading count for statistics
        self.reading_count = 0
        self.total_temp = 0.0

        self.get_logger().info('🔍 Temp Monitor Node started!')
        self.get_logger().info('   Listening on /temperature ...')
        self.get_logger().info(f'   Thresholds: DANGER >{TEMP_HIGH_DANGER}°C or <{TEMP_LOW_DANGER}°C')

    def analyze_temperature(self, msg):
        """Perform thermal telemetry analysis and state classification.

        This callback implements the \"Think\" phase of the Sense-Think-Act cycle.
        For each incoming temperature reading, it:

        1. Classifies the reading into a discrete state (OK, WARNING, DANGER)
        2. Updates running diagnostic statistics
        3. Triggers fault alerts for non-OK states
        4. Publishes state estimates to downstream nodes

        Args:
            msg (std_msgs/Float32): Incoming temperature telemetry (Celsius).

        Publishes:
            /alerts (std_msgs/String): Fault alert if state is WARNING/DANGER.
        """
        temp = msg.data
        self.reading_count += 1
        self.total_temp += temp
        avg = round(self.total_temp / self.reading_count, 1)

        # --- DETERMINE STATUS ---
        if temp >= TEMP_HIGH_DANGER:
            status = 'DANGER'
            emoji = '🔴'
            reason = f'Temperature too HIGH ({temp}°C >= {TEMP_HIGH_DANGER}°C)'

        elif temp >= TEMP_HIGH_WARNING:
            status = 'WARNING'
            emoji = '🟡'
            reason = f'Temperature slightly high ({temp}°C)'

        elif temp <= TEMP_LOW_DANGER:
            status = 'DANGER'
            emoji = '🔴'
            reason = f'Temperature too LOW ({temp}°C <= {TEMP_LOW_DANGER}°C)'

        elif temp <= TEMP_LOW_WARNING:
            status = 'WARNING'
            emoji = '🟡'
            reason = f'Temperature slightly low ({temp}°C)'

        else:
            status = 'OK'
            emoji = '🟢'
            reason = f'Temperature normal ({temp}°C)'

        # --- LOG locally ---
        self.get_logger().info(
            f'{emoji} Reading #{self.reading_count}: {temp}°C | '
            f'Status: {status} | Avg so far: {avg}°C'
        )

        # --- PUBLISH alert if not OK ---
        if status != 'OK':
            alert_msg = String()
            alert_msg.data = f'[{status}] {reason} | Reading #{self.reading_count}'
            self.alert_publisher.publish(alert_msg)
            self.get_logger().warn(f'🚨 Alert published: {alert_msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = TempMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()