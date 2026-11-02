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
    """Garante o comando CLI sem consultar pm, que pode gerar falso negativo."""
    pkg = shutil.which("pkg")
    if not pkg:
        raise RuntimeError("Gerenciador pkg do Termux não foi encontrado.")

    if not shutil.which("termux-storage-get"):
        print("\\nInstalando a API de linha de comando do Termux...")
        result = subprocess.run([pkg, "install", "-y", "termux-api"], check=False)
        if result.returncode != 0 or not shutil.which("termux-storage-get"):
            raise RuntimeError("Não foi possível instalar termux-api. Verifique a conexão e tente novamente.")

    # O próprio seletor confirmará se o complemento Android consegue responder.
    return True


def pick_image(destination: str | Path) -> Path | None:
    """Abre o seletor Android, diagnostica a resposta e valida a imagem recebida."""
    ensure_termux_api()

    picker = shutil.which("termux-storage-get")
    if not picker:
        raise RuntimeError("O comando termux-storage-get não foi encontrado após a instalação.")

    base = Path(destination).expanduser()
    base.parent.mkdir(parents=True, exist_ok=True)

    # Usar nome visível e extensão PNG: ambos os testes manuais do usuário
    # confirmaram que termux-storage-get grava corretamente nesse formato.
    temporary = Path.home() / f"NEXUS-IMAGE-{time.time_ns()}.png"
    print(f"\n[DIAGNÓSTICO] Comando: {picker}")
    print(f"[DIAGNÓSTICO] Arquivo temporário: {temporary}")
    print("[DIAGNÓSTICO] Aguardando a seleção no Android...")

    try:
        result = subprocess.run([picker, str(temporary)], check=False)
    except OSError as error:
        raise RuntimeError(f"Falha ao executar o seletor: {error}") from error

    exists = temporary.is_file()
    size = temporary.stat().st_size if exists else 0
    print(f"\n[DIAGNÓSTICO] Código de saída: {result.returncode}")
    print(f"[DIAGNÓSTICO] Arquivo criado: {'sim' if exists else 'não'}")
    print(f"[DIAGNÓSTICO] Tamanho recebido: {size} bytes")

    if not exists or size == 0:
        temporary.unlink(missing_ok=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"Seletor retornou código {result.returncode}; nenhum arquivo foi recebido em {temporary}."
            )
        raise RuntimeError(
            f"O seletor terminou sem erro, mas não criou o arquivo esperado: {temporary}"
        )

    try:
        Image = _pillow_image()
        with Image.open(temporary) as selected:
            print(f"[DIAGNÓSTICO] Formato detectado: {selected.format}")
            print(f"[DIAGNÓSTICO] Dimensões: {selected.width}x{selected.height}")
            selected.verify()
        print("[DIAGNÓSTICO] Validação Pillow: OK")
    except Exception as error:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"Arquivo recebido, mas não é uma imagem válida: {error}") from error

    target = base.with_name(f"{base.stem}-{time.time_ns()}.png")
    try:
        shutil.move(str(temporary), str(target))
    except OSError as error:
        raise RuntimeError(
            f"Imagem recebida e validada, mas não foi possível movê-la para {target}: {error}"
        ) from error

    print(f"[DIAGNÓSTICO] Arquivo final: {target}")
    return target
