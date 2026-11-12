from glob import glob
from setuptools import setup

package_name = 'mnemos_simulation'
setup(name=package_name, version='0.1.0', packages=[], data_files=[
    ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    ('share/' + package_name + '/worlds', glob('worlds/*')),
], zip_safe=True, maintainer='MNEMOS Contributors', maintainer_email='maintainers@example.com',
   description='MNEMOS Gazebo Harmonic assets.', license='Apache-2.0')
