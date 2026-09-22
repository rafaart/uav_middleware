from setuptools import find_packages, setup

package_name = 'middleware_bridge'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/middleware.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Rafael Santos Souza',
    maintainer_email='rafael.souza@example.com',
    description=(
        'Camada de integracao ROS2 do middleware IA-UAV. Plumbing apenas; '
        'a logica de decisao vive no pacote middleware_core (pip, sem ROS).'
    ),
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'image_converter_node = middleware_bridge.image_converter_node:main',
            'status_node = middleware_bridge.status_node:main',
            'detection_bridge_node = middleware_bridge.detection_bridge_node:main',
            'control_publisher_node = middleware_bridge.control_publisher_node:main',
        ],
    },
)
