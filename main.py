
#!/usr/bin/env python3
"""Termux Nexus — personalizador leve para Termux."""

from __future__ import annotations

import datetime
import json
import os
import platform
import shutil
import socket
import subprocess
from pathlib import Path

HOME = Path.home()
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config")) / "termux-nexus"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULTS = {
    "theme": "cyan",
    "banner": "COOLKID",
    "show_clock": True
}

COLORS = {
    "cyan": "\033[96m",
    "green": "\033[92m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "white": "\033[97m"
}

RESET = "\033[0m"


def load_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    try:
        saved = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return {**DEFAULTS, **saved}
    except (OSError, json.JSONDecodeError):
        return DEFAULTS.copy()


def save_config(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    CONFIG_FILE.write_text(
        json.dumps(cfg, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )


def paint(cfg):
    return COLORS.get(cfg.get("theme"), COLORS["cyan"])


def live_input(prompt_text, cfg):
    """Entrada com relógio dinâmico usando Prompt Toolkit."""

    if not cfg.get("show_clock", True):
        try:
            return input(prompt_text).strip()
        except EOFError:
            return "0"

    try:
        from prompt_toolkit import prompt
        from prompt_toolkit.styles import Style

        theme_colors = {
            "cyan": "#00ffff",
            "green": "#00ff66",
            "blue": "#5599ff",
            "magenta": "#ff55ff",
            "white": "#ffffff"
        }

        clock_color = theme_colors.get(
            cfg.get("theme"),
            "#00ffff"
        )

        style = Style.from_dict({
            "bottom-toolbar": f"fg:{clock_color} bg:#151515"
        })

        def clock_toolbar():
            now = datetime.datetime.now().astimezone()
            clock = now.strftime("%d/%m/%Y  •  %H:%M:%S %Z")

            return [
                ("class:bottom-toolbar", f"  {clock}  ")
            ]

        return prompt(
            prompt_text,
            bottom_toolbar=clock_toolbar,
            refresh_interval=1,
            style=style
        ).strip()

    except ImportError:
        print("Prompt Toolkit não encontrado. Usando entrada normal.")
        try:
            return input(prompt_text).strip()
        except EOFError:
            return "0"


def banner(cfg):
    c = paint(cfg)

    print(c + r"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║  ████████╗███████╗██████╗ ███╗   ███╗██╗   ██╗██╗  ██╗    ║
║     ██╔══╝██╔════╝██╔══██╗████╗ ████║██║   ██║╚██╗██╔╝    ║
║     ██║   █████╗  ██████╔╝██╔████╔██║██║   ██║ ╚███╔╝     ║
║     ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║   ██║ ██╔██╗     ║
║     ██║   ███████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██╔╝ ██╗    ║
║     ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝    ║
║                                                            ║
║                    TERMUX NEXUS  •  1.0.0                  ║
╚════════════════════════════════════════════════════════════╝
""" + RESET)

    label = cfg.get("banner", "NEXUS")[:24]
    print(c + f"  {label}" + RESET)
    print()


def pause():
    try:
        input("\nPressione Enter para voltar...")
    except EOFError:
        pass


def show_system(cfg):
    os.system("clear")
    banner(cfg)

    print("INFORMAÇÕES DO SISTEMA\n")
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Arquitetura: {platform.machine()}")
    print(f"Python: {platform.python_version()}")
    print(f"Host: {socket.gethostname()}")

    usage = shutil.disk_usage(HOME)
    print(f"Espaço livre: {usage.free // (1024**3)} GB")

    pause()


# ============================================================
# FFmpeg GLITCH VIDEO
# ============================================================

def ask_effect(cfg, description):
    answer = live_input(
        f"{description} [s/N]: ",
        cfg
    ).lower()

    return answer in ("s", "sim", "y", "yes")


def ensure_ffmpeg():
    """Verifica e instala automaticamente FFmpeg no Termux."""

    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return True

    os.system("clear")

    print("FFMPEG NÃO ENCONTRADO")
    print("\nO Termux Nexus precisa instalar o FFmpeg.")
    print("Iniciando instalação automática...\n")

    if not shutil.which("pkg"):
        print("Gerenciador de pacotes do Termux não encontrado.")
        return False

    try:
        subprocess.run(
            ["pkg", "update", "-y"],
            check=True
        )

        subprocess.run(
            ["pkg", "install", "ffmpeg", "-y"],
            check=True
        )

    except subprocess.CalledProcessError as error:
        print(f"\nFalha na instalação: {error}")
        print("Verifique sua conexão com a internet.")
        return False

    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        print("\nFFmpeg instalado com sucesso!")
        return True

    print("\nNão foi possível confirmar a instalação.")
    return False


def ffmpeg_glitch_video(cfg):
    os.system("clear")
    banner(cfg)

    print("FFMPEG GLITCH VIDEO")
    print("Modo manual • Intensidade extrema\n")

    if not ensure_ffmpeg():
    pause()
    return

ffmpeg = shutil.which("ffmpeg")

    print("Digite o caminho completo do vídeo.")
    print("Exemplo: /sdcard/Movies/video.mp4\n")

    input_path = live_input("Caminho do vídeo > ", cfg)

    if not input_path:
        print("\nNenhum arquivo selecionado.")
        pause()
        return

    video = Path(input_path).expanduser()

    if not video.is_file():
        print("\nArquivo não encontrado!")
        pause()
        return

    # Verificar se existe uma faixa de vídeo.
    try:
        probe = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_type",
                "-of", "csv=p=0",
                str(video)
            ],
            capture_output=True,
            text=True,
            check=True
        )

        if not probe.stdout.strip():
            print("\nO arquivo não contém uma faixa de vídeo válida.")
            pause()
            return

    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\nNão foi possível analisar o vídeo.")
        print("Verifique se o FFprobe está disponível.")
        pause()
        return

    # Efeitos visuais.
    video_effects = [
        (
            "RGB Split",
            "Separação extrema das cores RGB",
            "rgbashift=rh=24:rv=0:bh=-24:bv=0"
        ),
        (
            "Digital Noise",
            "Ruído digital intenso",
            "noise=alls=80:allf=t+u"
        ),
        (
            "Color Corruption",
            "Saturação e contraste extremos",
            "eq=contrast=2.0:saturation=3.0:gamma=0.7"
        ),
        (
            "Hue Distortion",
            "Distorção extrema de tonalidade",
            "hue=h=90:s=2"
        ),
        (
            "Negative",
            "Inversão das cores",
            "negate"
        ),
        (
            "Pixelation",
            "Pixelização pesada",
            "scale=iw/4:ih/4:flags=neighbor,scale=iw*4:ih*4:flags=neighbor"
        )
    ]

    # Efeitos sonoros.
    audio_effects = [
        (
            "Bitcrusher",
            "Redução extrema da qualidade digital",
            "acrusher=bits=4:mix=1"
        ),
        (
            "Echo",
            "Eco exagerado",
            "aecho=0.8:0.9:1000|1800:0.8|0.5"
        ),
        (
            "Lowpass",
            "Corte extremo das frequências altas",
            "lowpass=f=1200"
        ),
        (
            "Highpass",
            "Corte extremo das frequências baixas",
            "highpass=f=500"
        ),
        (
            "Distorted Sound",
            "Distorção e saturação sonora",
            "asoftclip=type=hard:threshold=0.3"
        )
    ]

    selected_video = []
    selected_audio = []

    os.system("clear")
    banner(cfg)

    print("SELEÇÃO DE EFEITOS VISUAIS")
    print("Responda S para ativar ou N para ignorar.\n")

    for name, description, filter_value in video_effects:
        print(f"\n[{name}]")
        if ask_effect(cfg, description):
            selected_video.append(filter_value)

    os.system("clear")
    banner(cfg)

    print("SELEÇÃO DE EFEITOS SONOROS")
    print("Responda S para ativar ou N para ignorar.\n")

    for name, description, filter_value in audio_effects:
        print(f"\n[{name}]")
        if ask_effect(cfg, description):
            selected_audio.append(filter_value)

    if not selected_video and not selected_audio:
        print("\nNenhum efeito foi selecionado.")
        pause()
        return

    # Criar nome de saída sem sobrescrever arquivos.
    default_output = video.with_name(
        video.stem + "_GLITCH.mp4"
    )

    print("\nARQUIVO DE SAÍDA")
    print(f"Destino sugerido: {default_output}")

    output_input = live_input(
        "\nNovo caminho (Enter para usar o sugerido) > ",
        cfg
    )

    output = (
        Path(output_input).expanduser()
        if output_input
        else default_output
    )

    if output.resolve() == video.resolve():
        print("\nO arquivo de saída não pode ser o próprio original.")
        pause()
        return

    if output.exists():
        print("\nEsse arquivo já existe. Escolha outro nome.")
        pause()
        return

    if output.suffix.lower() != ".mp4":
        output = output.with_suffix(".mp4")

        if output.exists():
            print("\nO arquivo de saída já existe.")
            pause()
            return

    output.parent.mkdir(parents=True, exist_ok=True)

    # Montar comando FFmpeg.
    command = [
        ffmpeg,
        "-hide_banner",
        "-i", str(video),
        "-map", "0:v:0",
        "-map", "0:a?",
    ]

    if selected_video:
        command.extend([
            "-vf", ",".join(selected_video)
        ])

    if selected_audio:
        command.extend([
            "-af", ",".join(selected_audio)
        ])

    command.extend([
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "96k",
        "-movflags", "+faststart",
        "-n",
        str(output)
    ])

    os.system("clear")
    banner(cfg)

    print("PROCESSAMENTO GLITCH")
    print(f"\nVídeo original: {video}")
    print(f"Arquivo final: {output}")

    print("\nEfeitos visuais:")
    for effect in selected_video:
        print(f"  + {effect}")

    print("\nEfeitos sonoros:")
    for effect in selected_audio:
        print(f"  + {effect}")

    print("\nIniciando FFmpeg...\n")

    try:
        result = subprocess.run(command)

        if result.returncode == 0 and output.exists():
            print("\nVídeo glitch criado com sucesso!")
            print(f"\nArquivo: {output}")
            print(f"Tamanho: {output.stat().st_size // 1024} KB")
        else:
            print("\nO FFmpeg encontrou um erro.")
            print("O arquivo original foi preservado.")

            if output.exists():
                output.unlink()

    except KeyboardInterrupt:
        print("\nProcessamento interrompido.")

        if output.exists():
            output.unlink()

    except Exception as error:
        print(f"\nErro inesperado: {error}")

        if output.exists():
            output.unlink()

    pause()


# ============================================================
# FERRAMENTAS
# ============================================================

def tools_menu(cfg):
    while True:
        os.system("clear")
        banner(cfg)

        print(
            "FERRAMENTAS\n"
            "[1] Listar arquivos\n"
            "[2] Testar conexão\n"
            "[3] Verificar FFmpeg\n"
            "[4] Informações do sistema\n"
            "[5] FFmpeg Glitch Video\n"
            "[0] Voltar"
        )

        choice = live_input("\nNexus/tools > ", cfg)

        if choice == "1":
            subprocess.run(["ls", "-lah"])
            pause()

        elif choice == "2":
            os.system("clear")

            result = subprocess.run(
                ["ping", "-c", "1", "-W", "3", "1.1.1.1"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            print(
                "Conexão respondeu."
                if result.returncode == 0
                else "Não foi possível confirmar a conexão."
            )

            pause()

        elif choice == "3":
            os.system("clear")

            found = shutil.which("ffmpeg")

            print(
                f"FFmpeg disponível em: {found}"
                if found
                else "FFmpeg não encontrado. Instale com: pkg install ffmpeg -y"
            )

            pause()

        elif choice == "4":
            show_system(cfg)

        elif choice == "5":
            ffmpeg_glitch_video(cfg)

        elif choice == "0":
            return


# ============================================================
# CONFIGURAÇÕES
# ============================================================

def settings(cfg):
    while True:
        os.system("clear")
        banner(cfg)

        print("CONFIGURAÇÕES\n")
        print(f"[1] Cor: {cfg['theme']}")
        print(f"[2] Texto personalizado: {cfg['banner']}")
        print(f"[3] Relógio: {'ligado' if cfg['show_clock'] else 'desligado'}")
        print("[4] Caixa de ferramentas")
        print("[5] Informações do sistema")
        print("[6] Restaurar padrões")
        print("[0] Sair")

        choice = live_input("\nNexus/config > ", cfg)

        if choice == "1":
            print("\nOpções: " + ", ".join(COLORS))

            value = input("Escolha uma cor: ").strip().lower()

            if value in COLORS:
                cfg["theme"] = value
                save_config(cfg)

        elif choice == "2":
            value = input(
                "Novo texto (máximo 24 caracteres): "
            ).strip()[:24]

            if value:
                cfg["banner"] = value
                save_config(cfg)

        elif choice == "3":
            cfg["show_clock"] = not cfg["show_clock"]
            save_config(cfg)

        elif choice == "4":
            tools_menu(cfg)

        elif choice == "5":
            show_system(cfg)

        elif choice == "6":
            cfg = DEFAULTS.copy()
            save_config(cfg)

        elif choice == "0":
            return


# ============================================================
# ATUALIZADOR
# ============================================================

def update_nexus(cfg):
    os.system("clear")
    banner(cfg)

    repo = Path.home() / "termux-nexus"

    print("ATUALIZADOR DO TERMUX NEXUS\n")

    if not (repo / ".git").exists():
        print("Repositório não encontrado!")
        print(f"Esperado em: {repo}")
        pause()
        return

    print("Verificando atualizações no GitHub...\n")

    try:
        subprocess.run(
            ["git", "-C", str(repo), "fetch", "origin"],
            check=True
        )

        local = subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            text=True
        ).strip()

        remote = subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "origin/main"],
            text=True
        ).strip()

        if local == remote:
            print("Você já está utilizando a versão mais recente!")
            pause()
            return

        print("Uma nova atualização foi encontrada!")
        answer = input("\nDeseja atualizar? [S/N] > ").strip().lower()

        if answer not in ("s", "sim"):
            print("\nAtualização cancelada.")
            pause()
            return

        print("\nBaixando atualização...\n")

        subprocess.run(
            ["git", "-C", str(repo), "pull", "--ff-only", "origin", "main"],
            check=True
        )

        print("\nInstalando arquivos atualizados...\n")

        subprocess.run(
            ["bash", str(repo / "install.sh")],
            check=True
        )

        print("\nAtualização concluída com sucesso!")
        print("Feche e abra novamente o Nexus para carregar tudo.")

    except subprocess.CalledProcessError as error:
        print(f"\nErro durante a atualização: {error}")
        print("Verifique sua conexão e possíveis alterações locais.")

    except FileNotFoundError:
        print("\nGit não encontrado. Instale com: pkg install git -y")

    pause()


# ============================================================
# MENU PRINCIPAL
# ============================================================

def main():
    cfg = load_config()

    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "config":
        settings(cfg)
        return

    while True:
        os.system("clear")
        banner(cfg)

        print("CENTRAL DE CONTROLE\n")
        print("[1] Personalização")
        print("[2] Caixa de ferramentas")
        print("[3] Informações do sistema")
        print("[4] Atualizar Termux Nexus")
        print("[0] Sair")

        choice = live_input("\nNexus > ", cfg)

        if choice == "1":
            settings(cfg)
            cfg = load_config()

        elif choice == "2":
            tools_menu(cfg)

        elif choice == "3":
            show_system(cfg)

        elif choice == "4":
            update_nexus(cfg)

        elif choice == "0":
            break


if __name__ == "__main__":
    main()
