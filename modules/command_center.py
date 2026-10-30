"""NEXUS COMMAND CENTER — shell interno com comandos controlados."""

import datetime
import json
import os
import platform
import shlex
import shutil
import socket
import subprocess
from pathlib import Path

HISTORY_FILE = Path(
    os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
) / "termux-nexus" / "command-history.json"

HELP = {
    "help": "Mostra os comandos disponíveis.",
    "clear": "Limpa a tela.",
    "time": "Mostra data e hora local.",
    "system": "Mostra informações básicas do sistema.",
    "ip": "Mostra o endereço IP local.",
    "dns <host>": "Consulta os endereços DNS de um domínio.",
    "ping <host>": "Testa a conectividade com um host.",
    "ascii <texto>": "Cria um pequeno banner ASCII.",
    "history": "Mostra o histórico desta central.",
    "exit": "Volta ao menu do Termux Nexus."
}


def _local_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("1.1.1.1", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def _load_history():
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _save_history(history):
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.write_text(
            json.dumps(history[-100:], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8"
        )
    except OSError:
        pass


def _ascii(text):
    width = min(max(len(text) + 4, 12), 70)
    print("+" + "-" * (width - 2) + "+")
    print("| " + text[:width - 4].center(width - 4) + " |")
    print("+" + "-" * (width - 2) + "+")


def _execute(parts):
    command = parts[0].lower()
    args = parts[1:]

    if command == "help":
        print("\nCOMANDOS DISPONÍVEIS")
        for name, description in HELP.items():
            print(f"  {name:<14} {description}")
    elif command == "clear":
        os.system("clear")
    elif command == "time":
        print(datetime.datetime.now().astimezone().strftime("%d/%m/%Y %H:%M:%S %Z"))
    elif command == "system":
        print(f"Sistema: {platform.system()} {platform.release()}")
        print(f"Arquitetura: {platform.machine()}")
        print(f"Python: {platform.python_version()}")
        print(f"Hostname: {socket.gethostname()}")
    elif command == "ip":
        print("IP local: " + _local_ip())
    elif command == "dns":
        if not args:
            print("Uso: dns exemplo.com")
            return
        try:
            addresses = sorted({
                item[4][0] for item in socket.getaddrinfo(
                    args[0], None, type=socket.SOCK_STREAM
                )
            })
            for address in addresses:
                print("  " + address)
        except socket.gaierror as error:
            print(f"Falha DNS: {error}")
    elif command == "ping":
        if not args:
            print("Uso: ping exemplo.com")
            return
        executable = shutil.which("ping")
        if not executable:
            print("Comando ping não encontrado.")
            return
        subprocess.run([executable, "-c", "4", "-W", "2", args[0]], check=False)
    elif command == "ascii":
        if not args:
            print("Uso: ascii Olá Nexus")
            return
        _ascii(" ".join(args))
    elif command == "history":
        history = _load_history()
        if not history:
            print("Histórico vazio.")
        else:
            for index, item in enumerate(history[-30:], 1):
                print(f"{index:>2}. {item}")
    elif command == "exit":
        return "exit"
    else:
        print(f"Comando desconhecido: {command}. Digite help.")
    return None


def run(cfg=None):
    history = _load_history()
    print("\033[96mNEXUS COMMAND CENTER\033[0m")
    print("Terminal interno iniciado. Digite help para ver os comandos.")
    print("Este ambiente não executa comandos arbitrários do sistema.")
    while True:
        try:
            raw = input("\n\033[96mNexus:\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo do Command Center.")
            break
        if not raw:
            continue
        try:
            parts = shlex.split(raw)
        except ValueError as error:
            print(f"Entrada inválida: {error}")
            continue
        history.append(raw)
        _save_history(history)
        if _execute(parts) == "exit":
            break
