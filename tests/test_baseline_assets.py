"""Fast, dependency-light contract tests for the Milestone 3–4 baseline."""
from pathlib import Path
import ast
import unittest
import xml.etree.ElementTree as ET

import yaml


ROOT = Path(__file__).resolve().parents[1]


class TestBaselineAssets(unittest.TestCase):
    def test_sdf_assets_are_well_formed_and_have_required_systems(self):
        for path in (ROOT / 'src/mnemos_simulation/worlds/lab.sdf',
                     ROOT / 'src/mnemos_simulation/worlds/mnemos_robot.sdf'):
            self.assertEqual(ET.parse(path).getroot().tag, 'sdf')
        robot = (ROOT / 'src/mnemos_simulation/worlds/mnemos_robot.sdf').read_text()
        for required in ('gz-sim-diff-drive-system', '<sensor name="lidar"',
                         '<sensor name="rgbd_camera"', '<topic>/cmd_vel</topic>'):
            self.assertIn(required, robot)

    def test_bridge_covers_navigation_and_slam_inputs(self):
        bridge = yaml.safe_load((ROOT / 'src/mnemos_bringup/config/bridge.yaml').read_text())
        topics = {entry['ros_topic_name']: entry['direction'] for entry in bridge}
        for topic in ('/clock', '/odom', '/scan', '/imu/data', '/camera/image',
                      '/camera/depth_image', '/camera/camera_info'):
            self.assertEqual(topics.get(topic), 'GZ_TO_ROS')
        self.assertEqual(topics.get('/cmd_vel'), 'ROS_TO_GZ')

    def test_nav2_has_obstacle_observations_and_inflation(self):
        params = yaml.safe_load((ROOT / 'src/mnemos_bringup/config/nav2_params.yaml').read_text())
        for scope in ('local_costmap', 'global_costmap'):
            configuration = params[scope][scope]['ros__parameters']
            self.assertIn('obstacle_layer', configuration['plugins'])
            self.assertIn('inflation_layer', configuration['plugins'])
            self.assertEqual(configuration['obstacle_layer']['scan']['topic'], '/scan')

    def test_launch_files_are_syntax_valid(self):
        for path in (ROOT / 'src/mnemos_bringup/launch').glob('*.launch.py'):
            ast.parse(path.read_text(), filename=str(path))

    def test_all_ros_packages_have_manifest_and_setup(self):
        for package in ('mnemos_robot_description', 'mnemos_simulation', 'mnemos_bringup', 'mnemos_slam',
                        'mnemos_control', 'mnemos_memory', 'mnemos_intervention', 'mnemos_reasoning',
                        'mnemos_evaluation'):
            directory = ROOT / 'src' / package
            self.assertTrue((directory / 'package.xml').is_file())
            self.assertTrue((directory / 'setup.py').is_file())


if __name__ == '__main__':
    unittest.main()
