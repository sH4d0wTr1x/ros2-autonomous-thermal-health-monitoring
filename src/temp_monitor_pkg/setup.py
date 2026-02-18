from setuptools import setup
import os
from glob import glob

package_name = 'temp_monitor_pkg'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        # Required for ROS2 to find the package
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include launch files
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Shariq',
    maintainer_email='shariq@example.com',
    description='Simple temperature monitoring system',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Format: 'command_name = package.file:main_function'
            'temp_sensor  = temp_monitor_pkg.temp_sensor:main',
            'temp_monitor = temp_monitor_pkg.temp_monitor:main',
            'logger       = temp_monitor_pkg.logger:main',
        ],
    },
)