#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # Get the package share directory
    mnemos_description_dir = get_package_share_directory('mnemos_robot_description')
    mnemos_simulation_dir = get_package_share_directory('mnemos_simulation')

    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time')
    world_name = LaunchConfiguration('world_name')

    # Declare launch arguments
    declare_use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation clock'
    )

    declare_world_arg = DeclareLaunchArgument(
        'world_name',
        default_value='lab_environment',
        description='Name of the world file to load'
    )

    # Launch Gazebo with the selected world
    gazebo_cmd = [
        'gz', 'server',
        os.path.join(mnemos_simulation_dir, 'worlds', f'{world_name}.world')
    ]

    # Spawn the robot in Gazebo
    robot_spawn_cmd = ExecuteProcess(
        cmd=['gz', 'model', '-s', '-f', os.path.join(mnemos_description_dir, 'mnemos_diff_drive.urdf')],
        output='screen'
    )

    # Launch RViz2
    rviz_config_dir = os.path.join(
        mnemos_description_dir, 'rviz', 'rviz2_config.rviz'
    )
    rviz_cmd = ExecuteProcess(
        cmd=['rviz2', '-d', rviz_config_dir],
        output='screen'
    )

    # Launch ROS 2 node to publish robot state
    robot_state_publisher_cmd = [
        os.path.join(mnemos_description_dir, 'launch', 'robot_state_publisher_launch.py')
    ]

    ld = LaunchDescription()
    ld.add_action(declare_use_sim_time_arg)
    ld.add_action(declare_world_arg)
    ld.add_action(ExecuteProcess(cmd=gazebo_cmd, output='screen'))
    ld.add_action(robot_spawn_cmd)
    # ld.add_action(rviz_cmd)
    # ld.add_action(robot_state_publisher_cmd)

    return ld