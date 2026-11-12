from setuptools import setup

package_name = 'mnemos_intervention'
setup(name=package_name, version='0.1.0', packages=[package_name], data_files=[
    ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    ('share/' + package_name, ['setup.cfg']),
], install_requires=['setuptools'], zip_safe=True, maintainer='MNEMOS Contributors',
   maintainer_email='maintainers@example.com', description='MNEMOS intervention capture.', license='Apache-2.0',
   entry_points={'console_scripts': ['intervention_recorder = mnemos_intervention.recorder:main']})
