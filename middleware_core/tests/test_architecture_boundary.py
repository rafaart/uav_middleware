"""Este teste é a garantia automatizada da alegação central da dissertação:
o núcleo é agnóstico a framework. Se algum dia alguém importar `rclpy`,
`cv2`, `mavros_msgs` ou qualquer mensagem ROS dentro de `middleware_core`,
o build deve falhar aqui — antes de virar um acoplamento oculto que só
apareceria na hora de tentar trocar de autopiloto ou de modelo de IA."""

import ast
import pathlib

FORBIDDEN_TOP_LEVEL_MODULES = {
    "rclpy",
    "rclpy.node",
    "cv2",
    "cv_bridge",
    "mavros_msgs",
    "sensor_msgs",
    "vision_msgs",
    "geometry_msgs",
    "std_msgs",
    "diagnostic_msgs",
    "launch",
    "launch_ros",
}


def _core_python_files() -> list[pathlib.Path]:
    core_dir = pathlib.Path(__file__).parent.parent / "middleware_core"
    return list(core_dir.rglob("*.py"))


def test_core_nao_importa_frameworks_externos():
    violations: list[str] = []

    for py_file in _core_python_files():
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_level = alias.name.split(".")[0]
                    if top_level in FORBIDDEN_TOP_LEVEL_MODULES:
                        violations.append(f"{py_file.name}: 'import {alias.name}'")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top_level = node.module.split(".")[0]
                    if top_level in FORBIDDEN_TOP_LEVEL_MODULES:
                        violations.append(f"{py_file.name}: 'from {node.module} import ...'")

    assert not violations, (
        "Dependência de framework encontrada dentro de middleware_core "
        "(isso quebra o agnosticismo do núcleo):\n" + "\n".join(violations)
    )


def test_core_nao_tem_nenhuma_dependencia_externa_declarada():
    """Confirma que pyproject.toml não introduziu nenhuma dependência de
    runtime — o núcleo deve rodar só com a stdlib do Python."""
    pyproject = pathlib.Path(__file__).parent.parent / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    assert "dependencies = []" in content, (
        "pyproject.toml ganhou dependências de runtime — verifique se isso "
        "não introduz acoplamento a framework no núcleo."
    )
