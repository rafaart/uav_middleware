# uav_middleware

Middleware agnóstico ao modelo de IA e ao autopiloto para controle
autônomo de UAVs — implementação de referência da dissertação
"Desenvolvimento de middleware para integração de Inteligência Artificial
ao controle de voo autônomo de UAVs" (Rafael Santos Souza, PPGMC/UESC).

## Arquitetura em duas camadas

```
ros2_ws/src/middleware_bridge/   <- camada de integração ROS2 (plumbing)
middleware_core/                  <- núcleo de decisão (sem ROS/MAVROS/OpenCV)
```

O núcleo (`middleware_core`) não sabe que ROS2 existe. A camada de
integração (`middleware_bridge`) não toma nenhuma decisão — ela só
converte tipos ROS ↔ tipos do núcleo e aplica as checagens de segurança.
Essa separação é o que sustenta a alegação de que modelo de inferência e
autopiloto são componentes plenamente substituíveis (ver dissertação,
capítulo 5).

## Ordem de instalação

### 1. Núcleo (pode ser feito em qualquer máquina, sem ROS2 instalado)

```bash
cd middleware_core
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
```

Isso já deve rodar e passar (26 testes) mesmo sem nenhuma instalação de
ROS2, Gazebo ou MAVROS — é justamente a prova de que o núcleo é
independente de framework.

### 2. Pré-requisitos de sistema (ROS2 + simulação)

Ver `docs/VERSIONS.md` para a lista completa e o motivo de cada escolha.
Resumo:

- Ubuntu 24.04 LTS (Noble)
- ROS 2 Jazzy Jalisco
- Gazebo Harmonic
- `ArduPilot/ardupilot_gazebo` (plugin oficial, não o `khancyr/ardupilot_gazebo` legado)
- ArduPilot (SITL)
- MAVROS + MAVROS Extras
- Um wrapper ROS2 de YOLOv8 que publique `vision_msgs/Detection2DArray`
  (ex.: `Alpaca-zip/ultralytics_ros` — confirme a branch compatível com
  Jazzy antes de instalar)

### 3. Instalar o núcleo no ambiente Python do ROS2

**Antes** de rodar `colcon build`, instale `middleware_core` no mesmo
ambiente Python usado pelo ROS2 (não é um pacote `ament`, é uma lib pip
normal):

```bash
pip install -e /caminho/absoluto/para/middleware_core
```

### 4. Build do workspace ROS2

```bash
cd ros2_ws
colcon build --symlink-install
source install/setup.bash
```

### 5. Rodar

Com Gazebo + ArduPilot SITL + MAVROS + o nó YOLO já rodando em terminais
separados:

```bash
ros2 launch middleware_bridge middleware.launch.py
```

Parâmetros configuráveis via linha de comando (ex.: `kp_x:=0.3`) — ver
`ros2_ws/src/middleware_bridge/launch/middleware.launch.py`.

## Estrutura completa

```
uav_middleware/
├── middleware_core/                       # núcleo puro (sem ROS)
│   ├── pyproject.toml
│   ├── README.md
│   ├── middleware_core/
│   │   ├── __init__.py
│   │   ├── contracts.py                   # dataclasses do contrato de dados
│   │   ├── geometry.py                    # erro bbox <-> centro da imagem
│   │   ├── controller.py                  # ganho, zona morta, saturação
│   │   ├── state_machine.py               # FSM TRACKING/SEARCHING/LOST
│   │   └── pipeline.py                    # ponto único de entrada
│   └── tests/
│       ├── test_geometry.py
│       ├── test_controller.py
│       ├── test_state_machine.py
│       ├── test_pipeline.py
│       └── test_architecture_boundary.py  # garante o agnosticismo do núcleo
│
├── ros2_ws/src/middleware_bridge/         # camada de integração ROS2
│   ├── package.xml
│   ├── setup.py
│   ├── resource/middleware_bridge
│   ├── middleware_bridge/
│   │   ├── image_converter_node.py
│   │   ├── status_node.py
│   │   ├── detection_bridge_node.py
│   │   └── control_publisher_node.py
│   └── launch/middleware.launch.py
│
├── docs/
│   └── VERSIONS.md
├── .gitignore
├── LICENSE
└── README.md
```

## O que este esqueleto ainda NÃO faz

Estes pontos estão documentados como limitações no capítulo 5.4 da
dissertação e ficam para as próximas etapas do cronograma:

- Não realiza arm/disarm nem troca de modo automaticamente (assume que um
  piloto de segurança ou um nó externo já colocou o veículo em
  OFFBOARD/GUIDED e armado).
- Ganhos do controlador (`kp_x`, `kp_y`) são exploratórios, sem processo
  formal de sintonia.
- Failsafe implementado é elementar: timeout de comando e checagem de
  conexão/modo. Não trata desvio de obstáculos, RTL automático nem perda
  de detecção com múltiplos alvos concorrentes além de "maior confiança".
- Validado apenas com o par núcleo/testes unitários — a integração real
  com Gazebo + ArduPilot + YOLOv8 ainda precisa ser exercitada e
  documentada por você, seguindo o mesmo roteiro empírico usado nas
  reproduções do XTDrone e do DroneWrapper (capítulo 4).

## Licença

MIT — ver `LICENSE`.
