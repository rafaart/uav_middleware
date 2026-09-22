"""Assina detecções de QUALQUER modelo de IA que publique no contrato
vision_msgs/Detection2DArray (YOLOv8, uma versão anterior/posterior da
família, ou uma arquitetura de detecção distinta), converte para os tipos
do middleware_core, chama o núcleo de decisão (agnóstico a ROS) e publica
um comando NORMALIZADO (-1.0 a 1.0) em geometry_msgs/Twist.

Importante: este nó NÃO publica diretamente no setpoint do MAVROS. Essa
tradução final (escala para m/s reais + checagem de segurança de
armed/mode/connected) é responsabilidade do control_publisher_node, para
manter a lógica de segurança centralizada em um único lugar.
"""

import rclpy
from rclpy.node import Node
from vision_msgs.msg import Detection2DArray
from sensor_msgs.msg import CameraInfo
from geometry_msgs.msg import Twist

from middleware_core.contracts import BoundingBox, Detection, FrameContext
from middleware_core.controller import ControllerParams
from middleware_core.pipeline import TrackingPipeline


class DetectionBridgeNode(Node):
    def __init__(self) -> None:
        super().__init__('detection_bridge_node')

        self.declare_parameter('detections_topic', '/yolo/detections')
        self.declare_parameter('camera_info_topic', '/camera/camera_info')
        self.declare_parameter('output_topic', '/middleware/tracking_cmd')
        self.declare_parameter('kp_x', 0.5)
        self.declare_parameter('kp_y', 0.5)
        self.declare_parameter('deadzone', 0.05)
        self.declare_parameter('lost_timeout_frames', 15)

        params = ControllerParams(
            kp_x=self.get_parameter('kp_x').value,
            kp_y=self.get_parameter('kp_y').value,
            deadzone=self.get_parameter('deadzone').value,
        )
        self._pipeline = TrackingPipeline(
            controller_params=params,
            lost_timeout_frames=self.get_parameter('lost_timeout_frames').value,
        )

        self._image_width: int | None = None
        self._image_height: int | None = None

        self.create_subscription(
            CameraInfo,
            self.get_parameter('camera_info_topic').value,
            self._on_camera_info,
            10,
        )
        self.create_subscription(
            Detection2DArray,
            self.get_parameter('detections_topic').value,
            self._on_detections,
            10,
        )
        self._pub = self.create_publisher(
            Twist, self.get_parameter('output_topic').value, 10
        )

    def _on_camera_info(self, msg: CameraInfo) -> None:
        self._image_width = msg.width
        self._image_height = msg.height

    def _on_detections(self, msg: Detection2DArray) -> None:
        if self._image_width is None or self._image_height is None:
            self.get_logger().warn(
                'Aguardando CameraInfo para conhecer a resolução da imagem.',
                once=True,
            )
            return

        detections: list[Detection] = []
        for det in msg.detections:
            if not det.results:
                continue
            hyp = det.results[0].hypothesis
            class_id_str = str(hyp.class_id)
            detections.append(
                Detection(
                    bbox=BoundingBox(
                        x_center=det.bbox.center.position.x,
                        y_center=det.bbox.center.position.y,
                        width=det.bbox.size_x,
                        height=det.bbox.size_y,
                    ),
                    class_id=int(class_id_str) if class_id_str.isdigit() else -1,
                    class_name=class_id_str,
                    confidence=hyp.score,
                )
            )

        frame = FrameContext(
            image_width=self._image_width,
            image_height=self._image_height,
            timestamp_ns=self.get_clock().now().nanoseconds,
            detections=detections,
        )

        command = self._pipeline.process(frame)

        twist = Twist()
        twist.linear.x = command.vx
        twist.linear.y = command.vy
        twist.linear.z = command.vz
        twist.angular.z = command.yaw_rate
        self._pub.publish(twist)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DetectionBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
