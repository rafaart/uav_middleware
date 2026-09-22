"""Assina o status do autopiloto publicado pelo MAVROS (/mavros/state,
/mavros/battery) e o normaliza em middleware_core.contracts.AutopilotStatus
— o tipo que o núcleo entende, sem depender de mavros_msgs.

Publica também o status como diagnostic_msgs/DiagnosticStatus, para que
seja inspecionável via `ros2 topic echo` ou rqt sem precisar definir uma
mensagem .msg própria (o que exigiria um pacote de interfaces adicional
com geração via rosidl — deixado como possível evolução futura).
"""

import rclpy
from rclpy.node import Node
from diagnostic_msgs.msg import DiagnosticStatus, KeyValue
from mavros_msgs.msg import State
from sensor_msgs.msg import BatteryState

from middleware_core.contracts import AutopilotStatus


class StatusNode(Node):
    def __init__(self) -> None:
        super().__init__('status_node')

        self._armed = False
        self._mode = 'UNKNOWN'
        self._connected = False
        self._battery_pct: float | None = None

        self.create_subscription(State, '/mavros/state', self._on_state, 10)
        self.create_subscription(BatteryState, '/mavros/battery', self._on_battery, 10)

        self._pub = self.create_publisher(DiagnosticStatus, '/middleware/autopilot_status', 10)
        self.create_timer(1.0, self._publish_status)

    def _on_state(self, msg: State) -> None:
        self._armed = msg.armed
        self._mode = msg.mode
        self._connected = msg.connected

    def _on_battery(self, msg: BatteryState) -> None:
        if msg.percentage >= 0.0:
            self._battery_pct = msg.percentage * 100.0

    def current_status(self) -> AutopilotStatus:
        """Ponto de acesso reutilizável caso outro nó no mesmo processo
        precise do status já normalizado (ex.: em um nó composto)."""
        return AutopilotStatus(
            armed=self._armed,
            mode=self._mode,
            connected=self._connected,
            battery_pct=self._battery_pct,
        )

    def _publish_status(self) -> None:
        status = self.current_status()

        msg = DiagnosticStatus()
        msg.name = 'middleware/autopilot_status'
        msg.level = DiagnosticStatus.OK if status.connected else DiagnosticStatus.WARN
        msg.message = 'connected' if status.connected else 'disconnected'
        msg.values = [
            KeyValue(key='armed', value=str(status.armed)),
            KeyValue(key='mode', value=status.mode),
            KeyValue(key='connected', value=str(status.connected)),
            KeyValue(key='battery_pct', value=str(status.battery_pct)),
        ]
        self._pub.publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = StatusNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
