from glob import glob
from setuptools import setup

package_name = 'mnemos_robot_description'

setup(
    name=package_name,
    version='0.1.0',
    packages=[],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/urdf', glob('urdf/*')),
        ('share/' + package_name + '/rviz', glob('rviz/*')),
    ],
    zip_safe=True,
    maintainer='MNEMOS Contributors',
    maintainer_email='maintainers@example.com',
    description='MNEMOS robot description assets.',
    license='Apache-2.0',
)
