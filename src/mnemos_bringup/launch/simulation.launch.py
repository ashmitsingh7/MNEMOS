"""Launch Gazebo Harmonic, bridge its ROS interfaces, and publish robot frames."""
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    sim_share = Path(get_package_share_directory('mnemos_simulation'))
    description_share = Path(get_package_share_directory('mnemos_robot_description'))
    bridge_config = Path(get_package_share_directory('mnemos_bringup')) / 'config' / 'bridge.yaml'
    world = LaunchConfiguration('world')
    use_sim_time = LaunchConfiguration('use_sim_time')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(Path(get_package_share_directory('ros_gz_sim')) / 'launch' / 'gz_sim.launch.py')),
        launch_arguments={'gz_args': ['-r ', world]}.items(),
    )
    spawn = Node(
        package='ros_gz_sim', executable='create', output='screen',
        arguments=['-name', 'mnemos', '-file', str(sim_share / 'worlds' / 'mnemos_robot.sdf')],
    )
    bridge = Node(package='ros_gz_bridge', executable='parameter_bridge', output='screen',
                  parameters=[{'config_file': str(bridge_config)}])
    robot_description = (description_share / 'urdf' / 'mnemos.urdf').read_text()
    state_publisher = Node(
        package='robot_state_publisher', executable='robot_state_publisher', output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': use_sim_time}],
    )
    readiness = Node(package='mnemos_slam', executable='readiness_monitor', output='screen',
                     parameters=[{'use_sim_time': use_sim_time}])
    return LaunchDescription([
        DeclareLaunchArgument('world', default_value=str(sim_share / 'worlds' / 'lab.sdf'),
                              description='Absolute path to a Gazebo Harmonic SDF world.'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        gazebo, bridge, state_publisher, spawn, readiness,
        Node(package='tf2_ros', executable='static_transform_publisher', output='screen',
             arguments=['--frame-id', 'camera_link', '--child-frame-id', 'mnemos/base_link/rgbd_camera']),
        Node(package='tf2_ros', executable='static_transform_publisher', output='screen',
             arguments=['--frame-id', 'base_footprint', '--child-frame-id', 'base_link']),
    ])
