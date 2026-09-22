"""Recebe o comando NORMALIZADO (-1.0 a 1.0) publicado pelo
detection_bridge_node, aplica os intertravamentos de segurança mínimos
(veículo conectado, armado e em modo OFFBOARD/GUIDED) e só então traduz
para um setpoint de velocidade real (m/s, rad/s) no tópico que o MAVROS
espera.

Também implementa o failsafe elementar descrito na dissertação (seção
5.4): se nenhum comando novo chegar dentro do timeout configurado, publica
velocidade zero em vez de manter o último comando válido indefinidamente.

Manter essa lógica separada do nó de percepção (detection_bridge_node) é
proposital: segurança e escala de unidades ficam centralizadas em um único
lugar, mais fácil de auditar e de testar isoladamente.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped
from mavros_msgs.msg import State

ALLOWED_MODES = {'OFFBOARD', 'GUIDED'}


class ControlPublisherNode(Node):
    def __init__(self) -> None:
        super().__init__('control_publisher_node')

        self.declare_parameter('input_topic', '/middleware/tracking_cmd')
        self.declare_parameter('output_topic', '/mavros/setpoint_velocity/cmd_vel')
        self.declare_parameter('max_linear_speed', 1.0)  # m/s
        self.declare_parameter('max_yaw_rate', 0.5)  # rad/s
        self.declare_parameter('command_timeout_sec', 0.5)

        self._armed = False
        self._mode = 'UNKNOWN'
        self._connected = False
        self._last_cmd_time = None

        self.create_subscription(State, '/mavros/state', self._on_state, 10)
        self.create_subscription(
            Twist, self.get_parameter('input_topic').value, self._on_command, 10
        )
        self._pub = self.create_publisher(
            TwistStamped, self.get_parameter('output_topic').value, 10
        )

        timeout = self.get_parameter('command_timeout_sec').value
        self.create_timer(timeout, self._check_command_timeout)

    def _on_state(self, msg: State) -> None:
        self._armed = msg.armed
        self._mode = msg.mode
        self._connected = msg.connected

    def _is_safe_to_command(self) -> bool:
        return self._connected and self._armed and self._mode in ALLOWED_MODES

    def _on_command(self, msg: Twist) -> None:
        self._last_cmd_time = self.get_clock().now()

        if not self._is_safe_to_command():
            self.get_logger().warn(
                f'Comando bloqueado (armed={self._armed}, mode={self._mode}, '
                f'connected={self._connected}) — nenhum setpoint enviado.',
                throttle_duration_sec=2.0,
            )
            return

        self._publish_scaled(msg)

    def _publish_scaled(self, msg: Twist) -> None:
        max_v = self.get_parameter('max_linear_speed').value
        max_yaw = self.get_parameter('max_yaw_rate').value

        out = TwistStamped()
        out.header.stamp = self.get_clock().now().to_msg()
        out.header.frame_id = 'base_link'
        out.twist.linear.x = msg.linear.x * max_v
        out.twist.linear.y = msg.linear.y * max_v
        out.twist.linear.z = msg.linear.z * max_v
        out.twist.angular.z = msg.angular.z * max_yaw

        self._pub.publish(out)

    def _check_command_timeout(self) -> None:
        if self._last_cmd_time is None:
            return

        elapsed = (self.get_clock().now() - self._last_cmd_time).nanoseconds / 1e9
        timeout = self.get_parameter('command_timeout_sec').value

        if elapsed > timeout and self._is_safe_to_command():
            self.get_logger().warn(
                'Timeout de comando excedido — publicando velocidade zero.',
                throttle_duration_sec=2.0,
            )
            self._publish_scaled(Twist())  # todos os campos zerados por padrão


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ControlPublisherNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
