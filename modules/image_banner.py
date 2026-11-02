"""Renderiza imagens como banners ANSI True Color no terminal."""

from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path


def _pillow_image():
    try:
        from PIL import Image
        return Image
    except ImportError as error:
        raise RuntimeError(
            "A biblioteca Pillow não está instalada. Execute: pkg install python-pillow"
        ) from error


def render_image(path: str | Path, max_width: int | None = None) -> list[str]:
    """Converte a imagem em linhas de blocos RGB, limitadas à largura do terminal."""
    Image = _pillow_image()
    source = Path(path).expanduser()

    if not source.is_file():
        raise FileNotFoundError(f"Imagem não encontrada: {source}")

    terminal_width = shutil.get_terminal_size((80, 24)).columns
    # Margem de segurança para evitar quebra automática de linha.
    width_limit = max(12, min(terminal_width - 4, max_width or terminal_width - 4))

    with Image.open(source) as original:
        image = original.convert("RGB")

    source_width, source_height = image.size
    if source_width < 1 or source_height < 1:
        raise ValueError("A imagem está vazia.")

    # Células de terminal são aproximadamente duas vezes mais altas que largas.
    output_height = max(1, round(width_limit * source_height / source_width * 0.5))
    image.thumbnail((width_limit, output_height), Image.Resampling.LANCZOS)

    # Centraliza sem ampliar imagens pequenas e mantém as dimensões dentro do terminal.
    lines = []
    for y in range(image.height):
        parts = []
        for x in range(image.width):
            red, green, blue = image.getpixel((x, y))
            parts.append(f"\033[38;2;{red};{green};{blue}m█")
        parts.append("\033[0m")
        lines.append("".join(parts))

    return lines


def print_image_banner(path: str | Path) -> None:
    """Imprime banner sem prefixos laterais que poderiam provocar quebra de linha."""
    for line in render_image(path):
        print(line)


def _open_url(url: str) -> None:
    opener = shutil.which("termux-open-url")
    if opener:
        subprocess.run([opener, url], check=False)


def ensure_termux_api() -> bool:
    """Instala o pacote CLI e orienta a instalar o app Android complementar."""
    pkg = shutil.which("pkg")
    if not pkg:
        raise RuntimeError("Gerenciador pkg do Termux não foi encontrado.")

    if not shutil.which("termux-storage-get"):
        print("\\nInstalando a API de linha de comando do Termux...")
        result = subprocess.run([pkg, "install", "-y", "termux-api"], check=False)
        if result.returncode != 0 or not shutil.which("termux-storage-get"):
            raise RuntimeError("Não foi possível instalar termux-api. Verifique a conexão e tente novamente.")

    pm = shutil.which("pm")
    app_installed = False
    if pm:
        check = subprocess.run([pm, "path", "com.termux.api"], capture_output=True, text=True, check=False)
        app_installed = check.returncode == 0 and "package:" in check.stdout

    if not app_installed:
        print("\\nO aplicativo Termux:API não está instalado no Android.")
        print("Abrindo a página oficial para instalar o aplicativo complementar...")
        _open_url("https://f-droid.org/packages/com.termux.api/")
        print("Instale o Termux:API pela mesma fonte do seu Termux e depois volte ao NEXUS.")
        raise RuntimeError("O aplicativo complementar Termux:API ainda não está instalado.")
    return True


def pick_image(destination: str | Path) -> Path | None:
    """Abre o seletor Android e valida o arquivo de imagem realmente recebido."""
    if not ensure_termux_api():
        return None

    picker = shutil.which("termux-storage-get")
    if not picker:
        raise RuntimeError("O comando termux-storage-get não foi encontrado após a instalação.")

    base = Path(destination).expanduser()
    base.parent.mkdir(parents=True, exist_ok=True)
    # Extensão reconhecida pelo Android, sem sobrescrever o banner anterior.
    target = base.with_name(f"{base.stem}-{time.time_ns()}.png")
    try:
        result = subprocess.run([picker, str(target)], check=False)
    except OSError as error:
        raise RuntimeError(f"Não foi possível abrir o seletor do Android: {error}") from error

    if not target.is_file() or target.stat().st_size == 0:
        target.unlink(missing_ok=True)
        return None

    # Não confiar apenas no código de saída: validar o conteúdo recebido.
    try:
        Image = _pillow_image()
        with Image.open(target) as selected:
            selected.verify()
    except Exception as error:
        target.unlink(missing_ok=True)
        if result.returncode != 0:
            return None
        raise RuntimeError(f"O Android não entregou uma imagem válida: {error}") from error

    return target
