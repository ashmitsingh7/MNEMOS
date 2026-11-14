"""Start MNEMOS capture and advisory nodes beside a separately launched Nav2 stack."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    database_path = LaunchConfiguration('database_path')
    map_session_id = LaunchConfiguration('map_session_id')
    bag_reference = LaunchConfiguration('bag_reference')
    common = {'database_path': database_path, 'map_session_id': map_session_id,
              'bag_reference': bag_reference}
    return LaunchDescription([
        DeclareLaunchArgument('database_path', default_value='~/.ros/mnemos_episodes.sqlite3',
                              description='SQLite file storing auditable MNEMOS episodes.'),
        DeclareLaunchArgument('map_session_id', default_value='default',
                              description='Identifier for the map/session that produced these episodes.'),
        DeclareLaunchArgument('bag_reference', default_value='',
                              description='Raw ROS bag reference for auditability.'),
        Node(package='mnemos_control', executable='command_arbiter', output='screen'),
        Node(package='mnemos_intervention', executable='intervention_recorder', output='screen',
             parameters=[common]),
        Node(package='mnemos_reasoning', executable='memory_advisor', output='screen',
             parameters=[common]),
    ])
