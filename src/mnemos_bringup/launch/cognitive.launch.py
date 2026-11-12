"""Start MNEMOS capture and advisory nodes beside a separately launched Nav2 stack."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    database_path = LaunchConfiguration('database_path')
    common = {'database_path': database_path}
    return LaunchDescription([
        DeclareLaunchArgument('database_path', default_value='~/.ros/mnemos_episodes.sqlite3',
                              description='SQLite file storing auditable MNEMOS episodes.'),
        Node(package='mnemos_intervention', executable='intervention_recorder', output='screen',
             parameters=[common]),
        Node(package='mnemos_reasoning', executable='memory_advisor', output='screen',
             parameters=[common]),
    ])
