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
DEFAULTS = {"theme": "cyan", "banner": "COOLKID", "show_clock": True}
COLORS = {"cyan": "\033[96m", "green": "\033[92m", "blue": "\033[94m", "magenta": "\033[95m", "white": "\033[97m"}
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
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def paint(cfg):
    return COLORS.get(cfg.get("theme"), COLORS["cyan"])

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
    if cfg.get("show_clock", True):
        now = datetime.datetime.now().astimezone()
        print(c + "  " + now.strftime("%d/%m/%Y  •  %H:%M:%S %Z") + RESET)
    print()

def pause():
    input("\nPressione Enter para voltar...")

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

def tools_menu(cfg):
    while True:
        os.system("clear")
        banner(cfg)
        print("FERRAMENTAS\n[1] Listar arquivos\n[2] Testar conexão\n[3] Verificar FFmpeg\n[4] Informações do sistema\n[0] Voltar")
        choice = input("\nNexus/tools > ").strip()
        if choice == "1":
            subprocess.run(["ls", "-lah"]); pause()
        elif choice == "2":
            os.system("clear")
            result = subprocess.run(["ping", "-c", "1", "-W", "3", "1.1.1.1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Conexão respondeu." if result.returncode == 0 else "Não foi possível confirmar a conexão.")
            pause()
        elif choice == "3":
            os.system("clear")
            found = shutil.which("ffmpeg")
            print(f"FFmpeg disponível em: {found}" if found else "FFmpeg não encontrado. Instale com: pkg install ffmpeg")
            pause()
        elif choice == "4":
            show_system(cfg)
        elif choice == "0":
            return

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
        choice = input("\nNexus/config > ").strip()
        if choice == "1":
            print("\nOpções: " + ", ".join(COLORS))
            value = input("Escolha uma cor: ").strip().lower()
            if value in COLORS:
                cfg["theme"] = value; save_config(cfg)
        elif choice == "2":
            value = input("Novo texto (máximo 24 caracteres): ").strip()[:24]
            if value:
                cfg["banner"] = value; save_config(cfg)
        elif choice == "3":
            cfg["show_clock"] = not cfg["show_clock"]; save_config(cfg)
        elif choice == "4":
            tools_menu(cfg)
        elif choice == "5":
            show_system(cfg)
        elif choice == "6":
            cfg = DEFAULTS.copy(); save_config(cfg)
        elif choice == "0":
            return

        
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
        print("\nDeseja atualizar o Termux Nexus?")

        answer = input("[S/N] > ").strip().lower()

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
        print("\nGit não encontrado. Instale com: pkg install git")

    pause()



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

        choice = input("\nNexus > ").strip()

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
