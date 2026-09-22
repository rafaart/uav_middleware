# Versões recomendadas (verificado em setembro/2026)

Esta tabela existe porque a própria dissertação documenta, nos capítulos
4.1–4.3, como a dependência de versões específicas de ROS/framework levou
XTDrone e DroneWrapper à obsolescência prática. Trave estas versões desde
o primeiro commit e documente qualquer desvio.

| Componente | Versão / escolha | Motivo |
|---|---|---|
| Sistema operacional | Ubuntu 24.04 LTS (Noble) | Suporte padrão até 2029; plataforma Tier 1 para ROS2 Jazzy |
| ROS 2 | **Jazzy Jalisco** | LTS com suporte até maio de 2029 — folga confortável para o prazo de 6 meses do cronograma. Alternativa Kilted Kaiju também roda em Noble, mas seu suporte termina em nov/2026; Lyrical Luth (mais recente) tem Ubuntu 26.04 como plataforma primária e ecossistema de terceiros ainda imaturo nela |
| Simulador | Gazebo Harmonic | Pareamento oficial recomendado para ROS2 Jazzy |
| Plugin autopiloto↔simulador | `ArduPilot/ardupilot_gazebo` (repositório oficial da organização ArduPilot) | Substitui o antigo `khancyr/ardupilot_gazebo`; suporta Gazebo Garden e Harmonic. **Confirme no próprio repositório a distro Ubuntu suportada no momento da instalação** — documentação já observada pode estar defasada em relação ao pareamento Jazzy/Harmonic/Noble |
| Autopiloto | ArduPilot (branch estável mais recente, ex.: `Copter-4.x`) | Mesmo firmware SITL usado no protótipo do capítulo 5 |
| Ponte MAVLink↔ROS2 | MAVROS + MAVROS Extras | Instalar via `apt install ros-jazzy-mavros ros-jazzy-mavros-extras` e rodar o script `install_geographiclib_datasets.sh` |
| Detector de IA | YOLOv8 (Ultralytics) | Já usado no protótipo do capítulo 5 |
| Wrapper ROS2 do detector | `Alpaca-zip/ultralytics_ros` (ou nó próprio) | Publica `vision_msgs/Detection2DArray` — confirme se já existe branch compatível com Jazzy antes de instalar; documentação oficial confirma suporte a Humble |
| Contrato de detecção | `vision_msgs/Detection2DArray` | Mesmo contrato citado na dissertação como "amplamente utilizado por wrappers ROS2 de modelos da família YOLO" |
| Conversão de imagem | `cv_bridge` | Pacote padrão ROS2 |
| Linguagem do núcleo | Python 3.12 | Padrão do Ubuntu 24.04, evita conflito de ambiente virtual com o Python usado pelo ROS2 |
| Build system ROS2 | `colcon` + `ament_python` | |
| Testes | `pytest` (núcleo) + `launch_testing` (integração, a implementar) | |

## Checklist ao montar o ambiente do zero

1. Instalar Ubuntu 24.04.
2. Instalar ROS2 Jazzy (desktop completo, para ter RViz2 disponível).
3. Instalar Gazebo Harmonic (geralmente já vem com `ros-jazzy-desktop` via `ros_gz`, mas confirme a versão exata).
4. Clonar e compilar `ArduPilot/ardupilot_gazebo` — documentar o commit/tag usado.
5. Clonar e configurar ArduPilot (SITL) — documentar a tag usada.
6. Instalar MAVROS via apt (não compilar do source, salvo necessidade).
7. Instalar o wrapper YOLO escolhido — documentar a branch/commit.
8. `pip install -e ./middleware_core` no ambiente Python do ROS2.
9. `colcon build --symlink-install` em `ros2_ws/`.
10. Registrar tudo isso (passos 1–9) em um script versionado (ex.:
    `scripts/setup_environment.sh`) assim que validado manualmente —
    reprodutibilidade documentada é exatamente o que faltou nas
    reproduções do XTDrone/DroneWrapper relatadas na dissertação.
