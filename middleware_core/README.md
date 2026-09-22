# middleware_core

Núcleo de decisão do middleware, **sem nenhuma dependência de ROS2, MAVROS
ou OpenCV**. Ele só conhece dataclasses simples (veja `contracts.py`) e
funções puras. Essa restrição é proposital e é verificada por um teste
automatizado (`tests/test_architecture_boundary.py`) que falha o build se
qualquer módulo aqui dentro importar `rclpy`, `cv2`, `mavros_msgs` etc.

É essa separação que permite trocar o autopiloto (PX4 ↔ ArduPilot) ou o
modelo de inferência (YOLOv8 ↔ outro) sem tocar em uma linha deste pacote.

## Instalação (modo editável, para desenvolvimento)

```bash
cd middleware_core
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Rodar os testes

```bash
pytest -v
```

## Estrutura

- `contracts.py` — os tipos de dado que atravessam a fronteira núcleo ↔
  integração ROS2 (entrada: `Detection`, `FrameContext`, `AutopilotStatus`;
  saída: `NavigationCommand`, `TrackerState`).
- `geometry.py` — cálculo do erro normalizado entre o centro do bounding
  box e o centro da imagem.
- `controller.py` — tradução do erro em comando (ganho proporcional, zona
  morta, saturação).
- `state_machine.py` — máquina de estados de rastreamento
  (`TRACKING` / `SEARCHING` / `LOST`) e seleção de alvo entre múltiplas
  detecções.
- `pipeline.py` — orquestra os três módulos acima em um único ponto de
  entrada (`TrackingPipeline.process`), que é o que a camada de
  integração ROS2 efetivamente chama.

## Uso pela camada de integração (`middleware_bridge`)

O pacote ROS2 em `ros2_ws/src/middleware_bridge` importa este pacote como
uma dependência Python normal. Antes de rodar `colcon build`, instale-o no
mesmo ambiente Python usado pelo ROS2:

```bash
pip install -e /caminho/para/middleware_core
```
