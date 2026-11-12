"""Run Nav2 against a saved MNEMOS map; simulation is optional."""
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    bringup_share = Path(get_package_share_directory('mnemos_bringup'))
    nav2_launch = Path(get_package_share_directory('nav2_bringup')) / 'launch' / 'bringup_launch.py'
    params = bringup_share / 'config' / 'nav2_params.yaml'
    map_path = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    with_simulation = LaunchConfiguration('with_simulation')
    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(bringup_share / 'launch' / 'simulation.launch.py')),
        condition=IfCondition(with_simulation), launch_arguments={'use_sim_time': use_sim_time}.items(),
    )
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(nav2_launch)),
        launch_arguments={'map': map_path, 'params_file': str(params), 'use_sim_time': use_sim_time,
                          'autostart': 'true'}.items(),
    )
    return LaunchDescription([
        DeclareLaunchArgument('map', description='Absolute path to a Nav2 map YAML file.'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('with_simulation', default_value='true',
                              description='Start Gazebo and the MNEMOS robot before Nav2.'),
        simulation, nav2,
    ])
