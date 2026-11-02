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


TERMUX_API_DOWNLOAD = "https://f-droid.org/packages/com.termux.api/"


def ensure_termux_api() -> None:
    """Instala o pacote CLI e orienta a instalação do complemento Android."""
    if not shutil.which("termux-storage-get"):
        pkg = shutil.which("pkg")
        if not pkg:
            raise RuntimeError("O comando pkg não foi encontrado no Termux.")
        print("\\nInstalando as ferramentas Termux:API...")
        result = subprocess.run([pkg, "install", "-y", "termux-api"], check=False)
        if result.returncode != 0 or not shutil.which("termux-storage-get"):
            raise RuntimeError("Não foi possível instalar o pacote termux-api.")

    pm = shutil.which("pm")
    companion_installed = False
    if pm:
        try:
            check = subprocess.run([pm, "path", "com.termux.api"], capture_output=True, text=True, check=False)
            companion_installed = check.returncode == 0 and "package:" in check.stdout
        except OSError:
            pass

    if not companion_installed:
        print("\\nO aplicativo complementar Termux:API não foi encontrado.")
        print("Abrindo a página oficial para instalar o complemento...")
        opener = shutil.which("termux-open-url")
        if opener:
            subprocess.run([opener, TERMUX_API_DOWNLOAD], check=False)
        else:
            am = shutil.which("am")
            if am:
                subprocess.run([am, "start", "-a", "android.intent.action.VIEW", "-d", TERMUX_API_DOWNLOAD], check=False)
        raise RuntimeError("Instale o aplicativo complementar e tente novamente.")


def pick_image(destination: str | Path) -> Path | None:
    """Abre o seletor do Android e confirma a imagem pelo arquivo gravado."""
    ensure_termux_api()
    picker = shutil.which("termux-storage-get")
    if not picker:
        raise RuntimeError("termux-storage-get não ficou disponível após a instalação.")

    base = Path(destination).expanduser()
    base.parent.mkdir(parents=True, exist_ok=True)
    target = base.with_name(f"{base.stem}-{time.time_ns()}{base.suffix}")
    try:
        result = subprocess.run([picker, str(target)], check=False)
    except OSError as error:
        raise RuntimeError(f"Não foi possível abrir o seletor: {error}") from error

    # O arquivo é a confirmação mais confiável; não descarte uma imagem válida
    # apenas porque uma versão do comando retornou um código diferente de zero.
    if not target.is_file() or target.stat().st_size == 0:
        target.unlink(missing_ok=True)
        if result.returncode != 0:
            raise RuntimeError("O seletor não retornou uma imagem. Confira a instalação do Termux:API.")
        return None
    return target
