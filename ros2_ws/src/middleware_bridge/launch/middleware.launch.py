"""Sobe os quatro nós do middleware_bridge com parâmetros configuráveis
por linha de comando, ex.:

    ros2 launch middleware_bridge middleware.launch.py kp_x:=0.3 max_linear_speed:=0.8

Pré-requisitos (não gerenciados por este launch file):
  - Gazebo + ardupilot_gazebo + `sim_vehicle.py` já rodando
  - MAVROS já conectado ao SITL
  - Um nó de detecção (ex.: ultralytics_ros) publicando em /yolo/detections
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument('camera_topic', default_value='/camera/image_raw'),
            DeclareLaunchArgument('camera_info_topic', default_value='/camera/camera_info'),
            DeclareLaunchArgument('detections_topic', default_value='/yolo/detections'),
            DeclareLaunchArgument('kp_x', default_value='0.5'),
            DeclareLaunchArgument('kp_y', default_value='0.5'),
            DeclareLaunchArgument('deadzone', default_value='0.05'),
            DeclareLaunchArgument('lost_timeout_frames', default_value='15'),
            DeclareLaunchArgument('max_linear_speed', default_value='1.0'),
            DeclareLaunchArgument('max_yaw_rate', default_value='0.5'),
            DeclareLaunchArgument('command_timeout_sec', default_value='0.5'),
            Node(
                package='middleware_bridge',
                executable='image_converter_node',
                name='image_converter_node',
                output='screen',
                parameters=[{'input_topic': LaunchConfiguration('camera_topic')}],
            ),
            Node(
                package='middleware_bridge',
                executable='status_node',
                name='status_node',
                output='screen',
            ),
            Node(
                package='middleware_bridge',
                executable='detection_bridge_node',
                name='detection_bridge_node',
                output='screen',
                parameters=[
                    {
                        'camera_info_topic': LaunchConfiguration('camera_info_topic'),
                        'detections_topic': LaunchConfiguration('detections_topic'),
                        'kp_x': LaunchConfiguration('kp_x'),
                        'kp_y': LaunchConfiguration('kp_y'),
                        'deadzone': LaunchConfiguration('deadzone'),
                        'lost_timeout_frames': LaunchConfiguration('lost_timeout_frames'),
                    }
                ],
            ),
            Node(
                package='middleware_bridge',
                executable='control_publisher_node',
                name='control_publisher_node',
                output='screen',
                parameters=[
                    {
                        'max_linear_speed': LaunchConfiguration('max_linear_speed'),
                        'max_yaw_rate': LaunchConfiguration('max_yaw_rate'),
                        'command_timeout_sec': LaunchConfiguration('command_timeout_sec'),
                    }
                ],
            ),
        ]
    )
