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
    """Renderiza dois pixels por caractere usando ANSI True Color."""
    Image = _pillow_image()
    source = Path(path).expanduser()

    if not source.is_file():
        raise FileNotFoundError(f"Imagem não encontrada: {source}")

    terminal_width = shutil.get_terminal_size((80, 24)).columns
    # Margem de segurança para evitar quebra automática de linha.
    width_limit = max(12, min(terminal_width - 4, max_width or terminal_width - 4))

    with Image.open(source) as original:
        image = original.convert("RGBA")

    source_width, source_height = image.size
    if source_width < 1 or source_height < 1:
        raise ValueError("A imagem está vazia.")

    # Transparência é composta sobre preto, como o fundo padrão do NEXUS.
    background = Image.new("RGBA", image.size, (0, 0, 0, 255))
    image = Image.alpha_composite(background, image).convert("RGB")

    # Um caractere de terminal tem aproximadamente metade da largura da altura.
    # Com dois pixels por caractere (▀), cada pixel fica visualmente quase quadrado.
    output_height = max(1, round(width_limit * source_height / source_width))
    image = image.resize((width_limit, output_height), Image.Resampling.LANCZOS)

    lines = []
    black = (0, 0, 0)
    for y in range(0, image.height, 2):
        parts = []
        for x in range(image.width):
            top = image.getpixel((x, y))
            bottom = image.getpixel((x, y + 1)) if y + 1 < image.height else black
            red, green, blue = top
            bg_red, bg_green, bg_blue = bottom
            parts.append(
                f"\033[38;2;{red};{green};{blue};"
                f"48;2;{bg_red};{bg_green};{bg_blue}m▀"
            )
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

    print(f"\n[DIAGNÓSTICO] Código de saída inicial: {result.returncode}")
    if result.returncode != 0:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(
            f"O comando do seletor terminou com código {result.returncode}."
        )

    # O Termux:API pode iniciar a Activity Android e devolver o controle ao
    # processo antes de StorageActivity terminar a cópia do conteúdo escolhido.
    # Aguarda o arquivo aparecer e estabilizar, em vez de verificar cedo demais.
    print("[DIAGNÓSTICO] Aguardando o Android concluir a cópia...")
    deadline = time.monotonic() + 120
    last_size = -1
    stable_checks = 0
    while time.monotonic() < deadline:
        if temporary.is_file():
            current_size = temporary.stat().st_size
            if current_size > 0 and current_size == last_size:
                stable_checks += 1
                if stable_checks >= 3:
                    break
            else:
                stable_checks = 0
            last_size = current_size
        time.sleep(0.25)

    exists = temporary.is_file()
    size = temporary.stat().st_size if exists else 0
    print(f"[DIAGNÓSTICO] Arquivo criado: {'sim' if exists else 'não'}")
    print(f"[DIAGNÓSTICO] Tamanho recebido: {size} bytes")

    if not exists or size == 0:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(
            "O Android não entregou o arquivo em até 120 segundos. "
            "Verifique se a seleção foi concluída ou cancelada."
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
