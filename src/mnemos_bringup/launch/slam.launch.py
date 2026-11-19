"""Run RGB-D RTAB-Map SLAM against an already running MNEMOS simulation."""
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    rtabmap_launch = Path(get_package_share_directory('rtabmap_launch')) / 'launch' / 'rtabmap.launch.py'
    use_sim_time = LaunchConfiguration('use_sim_time')
    database_path = LaunchConfiguration('database_path')
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(rtabmap_launch)),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'frame_id': 'base_footprint',
            'odom_topic': '/odom',
            'rgb_topic': '/camera/image',
            'depth_topic': '/camera/depth_image',
            'camera_info_topic': '/camera/camera_info',
            'approx_sync': 'true',
            'queue_size': '30',
            'Rtabmap/DatabasePath': database_path,
            'Rtabmap/DetectionRate': '1.0',
            'Grid/FromDepth': 'true',
            'Grid/CellSize': '0.05',
        }.items(),
    )
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('database_path', default_value='~/.ros/mnemos_slam.db',
                              description='RTAB-Map database path; delete it to begin a clean mapping run.'),
        slam,
    ])
