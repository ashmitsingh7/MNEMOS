"""Compose one simulation with optional SLAM, Nav2, and cognitive nodes."""
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    bringup_share = Path(get_package_share_directory('mnemos_bringup'))
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_path = LaunchConfiguration('map')
    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(bringup_share / 'launch' / 'simulation.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
    )
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(bringup_share / 'launch' / 'slam.launch.py')),
        condition=UnlessCondition(LaunchConfiguration('with_navigation')),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
    )
    cognitive = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(bringup_share / 'launch' / 'cognitive.launch.py')),
    )
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(bringup_share / 'launch' / 'navigation.launch.py')),
        condition=IfCondition(LaunchConfiguration('with_navigation')),
        launch_arguments={
            'map': map_path, 'use_sim_time': use_sim_time, 'with_simulation': 'false',
        }.items(),
    )
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('with_navigation', default_value='false'),
        DeclareLaunchArgument('map', default_value='',
                              description='Saved map YAML, required when with_navigation:=true.'),
        simulation, slam, cognitive, navigation,
    ])
