# examples/ — demonstração sem ROS2, MAVROS, YOLO ou simulador

Estes scripts existem para provar, na prática e durante a defesa, que o
núcleo do middleware funciona isoladamente. Eles só importam
`middleware_core` — nenhum outro processo (Gazebo, ArduPilot, MAVROS,
YOLO) precisa estar rodando.

## Não precisa nem instalar o pacote

Os dois scripts já resolvem o import sozinhos, mesmo sem `pip install`.
Basta ter Python 3.10+ e rodar:

```bash
python examples/demo_scripted.py
```

ou

```bash
python examples/demo_interactive.py
```

(Se você já instalou `middleware_core` via `pip install -e ".[dev]"`,
funciona do mesmo jeito — o script usa a versão instalada nesse caso.)

## `demo_scripted.py` — sequência fixa, ideal para apresentar

Roda um cenário pré-definido (`SCENARIO`, no topo do arquivo) e imprime,
para cada frame sintético, uma visualização em texto da imagem + o
comando de navegação gerado pelo núcleo. O cenário cobre de propósito:

- alvo centralizado → comando neutro
- alvo se afastando do centro → comando de correção proporcional
- 5 frames seguidos sem detecção → transição `TRACKING → SEARCHING → LOST`
- alvo reaparecendo → volta a `TRACKING`
- duas detecções no mesmo frame → o núcleo escolhe a de maior confiança

Para editar o cenário, basta mudar a lista `SCENARIO` no arquivo — cada
item é `(rótulo, [(x, y, confiança), ...])`.

## `demo_interactive.py` — você digita, o núcleo responde

Um laço interativo: você digita a posição `x y` do "alvo detectado" (em
pixels, numa imagem simulada de 640x480) e o script imprime na hora o
comando gerado. Digite `vazio` para simular um frame sem detecção, e
`sair` para encerrar. Bom para responder perguntas ao vivo do tipo "e se
o alvo estivesse aqui?" sem precisar reescrever código.

## `demo_video.py` — gera um vídeo (mp4 + gif) da demonstração

Dependências extras, só para este script (não fazem parte do núcleo nem
dos outros demos):

```bash
pip install matplotlib "imageio[ffmpeg]"
```

O extra `[ffmpeg]` baixa automaticamente um binário **portátil** de
ffmpeg na primeira execução — não precisa instalar ffmpeg no sistema.

```bash
python examples/demo_video.py
```

Gera `examples/output/tracking_demo.mp4` e `tracking_demo.gif`: uma
trajetória sintética de ~150 frames em que o alvo se move pela imagem e
some por um trecho no meio, para mostrar visualmente a transição
`TRACKING → SEARCHING → LOST → TRACKING`. Em cada frame:

- `+` branco = centro da imagem (referência)
- quadrado ciano = bounding box do alvo "detectado"
- seta amarela = comando de correção gerado pelo núcleo, na direção certa
- texto no topo = frame, estado (colorido: verde/amarelo/vermelho) e vx/vy

Para editar a trajetória (velocidade, amplitude, quando o alvo "some"),
edite a função `build_trajectory()` no topo do arquivo.

O repositório já vem com um exemplo pronto em `output/` para você
conferir sem precisar rodar nada primeiro.

## O que isso prova (e o que não prova)

Prova que a lógica de decisão (geometria → controlador → máquina de
estados) funciona corretamente de forma isolada, sem qualquer dependência
de framework — exatamente a alegação central da dissertação.

Não prova, e não deveria ser apresentado como provando, que o sistema voa
de verdade: a integração com ROS2/MAVROS/Gazebo/YOLO (pasta
`ros2_ws/src/middleware_bridge`) ainda precisa ser validada à parte, como
já está descrito nas limitações do capítulo 5.4.
