"""Converte imagens do tópico da câmera para uma codificação OpenCV
normalizada (bgr8) via CvBridge e republica.

Esta é uma das três responsabilidades isoladas da camada de integração
descritas na dissertação (seção 5.1): conversão de imagem, leitura do
status do autopiloto (status_node.py) e assinatura de detecções
(detection_bridge_node.py). O detector de IA (ex.: YOLO) hoje consome a
imagem crua diretamente do driver/simulador; este nó existe para
desacoplar futuros consumidores baseados em visão computacional (SLAM,
odometria visual etc.) da codificação nativa publicada pela câmera,
evitando repetir a conversão CvBridge em cada novo módulo — o mesmo tipo
de conversão "pequena isoladamente, mas recorrente" apontada como
problema recorrente na seção de Trabalhos Relacionados.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


class ImageConverterNode(Node):
    def __init__(self) -> None:
        super().__init__('image_converter_node')

        self.declare_parameter('input_topic', '/camera/image_raw')
        self.declare_parameter('output_topic', '/middleware/image_cv')

        input_topic = self.get_parameter('input_topic').get_parameter_value().string_value
        output_topic = self.get_parameter('output_topic').get_parameter_value().string_value

        self._bridge = CvBridge()
        self._sub = self.create_subscription(Image, input_topic, self._on_image, 10)
        self._pub = self.create_publisher(Image, output_topic, 10)

        self.get_logger().info(f'Convertendo {input_topic} -> {output_topic} (bgr8)')

    def _on_image(self, msg: Image) -> None:
        try:
            cv_image = self._bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except CvBridgeError as exc:
            self.get_logger().warn(f'Falha ao converter imagem: {exc}', throttle_duration_sec=5.0)
            return

        out_msg = self._bridge.cv2_to_imgmsg(cv_image, encoding='bgr8')
        out_msg.header = msg.header
        self._pub.publish(out_msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ImageConverterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
