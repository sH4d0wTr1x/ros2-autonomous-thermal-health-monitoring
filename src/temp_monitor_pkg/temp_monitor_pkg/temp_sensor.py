"""Temperature Telemetry Acquisition Node.

This module implements a telemetry sensor node for a distributed thermal
monitoring system. The node simulates a hardware temperature sensor,
acquiring periodic thermal readings and publishing them to a ROS 2 topic
for downstream processing by state estimation nodes.

Architecture Role:
    Publisher (Telemetry Source) in a Sense-Think-Act distributed system.

Published Topics:
    /temperature (std_msgs/Float32): Raw thermal telemetry in Celsius (°C).
        Update frequency: 2 seconds.
        Sensor simulation: 70% normal (18-28°C), 15% warning (5-15°C),
        15% critical (35-45°C).

Typical Usage:
    ros2 launch temp_monitor_pkg monitor.launch.py
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import random


class TempSensor(Node):
    """Temperature telemetry sensor node.

    Simulates a thermal sensor on an autonomous platform, publishing
    periodic temperature readings to enable distributed fault detection
    and state estimation in the monitoring network.
    """

    def __init__(self):
        # 'temp_sensor' is the name of this node — visible in ros2 node list
        super().__init__('temp_sensor')

        # --- CREATE PUBLISHER ---
        # Arguments: (message_type, topic_name, queue_size)
        # Queue size 10 = keep last 10 messages if subscriber is slow
        self.publisher_ = self.create_publisher(Float32, '/temperature', 10)

        # --- CREATE TIMER ---
        # Call self.publish_temperature every 2.0 seconds
        self.timer = self.create_timer(2.0, self.publish_temperature)

        self.get_logger().info('🌡️  Temp Sensor Node started! Publishing to /temperature every 2s')

    def publish_temperature(self):
        """Publish thermal telemetry reading.

        This callback executes every 2 seconds, acquiring a simulated
        temperature reading and broadcasting it to subscriber nodes.
        Maintains realistic thermal distribution with occasional
        anomalies for fault detection testing.
        """

        msg = Float32()

        # Simulate realistic temperature readings:
        # Normal room: 18-25°C, occasionally spikes to 35-45°C (danger zone)
        roll = random.random()
        if roll < 0.15:
            # 15% chance of a high temperature spike (danger!)
            msg.data = round(random.uniform(35.0, 45.0), 1)
        elif roll < 0.30:
            # 15% chance of a low temperature (warning)
            msg.data = round(random.uniform(5.0, 15.0), 1)
        else:
            # 70% chance of normal temperature
            msg.data = round(random.uniform(18.0, 28.0), 1)

        # Publish the message to /temperature topic
        self.publisher_.publish(msg)
        self.get_logger().info(f'📤 Published temperature: {msg.data}°C')


def main(args=None):
    rclpy.init(args=args)           # Initialize ROS2 communication
    node = TempSensor()             # Create our node
    rclpy.spin(node)                # Keep node alive and listening
    node.destroy_node()             # Cleanup when done
    rclpy.shutdown()                # Shut down ROS2


if __name__ == '__main__':
    main()