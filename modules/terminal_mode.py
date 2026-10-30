"""NEXUS TERMINAL — modo de comandos integrado ao Termux."""

import datetime
import difflib
import os
import shlex
import shutil
import subprocess
from pathlib import Path


RESET = "\033[0m"
CYAN = "\033[96m"
DIM = "\033[90m"

UNKNOWN_ART = r"""
   █ █   █ █
    █     █
   █ █   █ █  

      ███
     █    █
    █      █
"""


def _clear():
    os.system("clear")


def _command_candidates():
    candidates = set()
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not directory:
            continue
        try:
            candidates.update(
                item.name for item in Path(directory).iterdir()
                if item.is_file() and os.access(item, os.X_OK)
            )
        except OSError:
            continue

    candidates.update({
        "alias", "bg", "bind", "break", "builtin", "caller", "cd",
        "command", "compgen", "continue", "declare", "dirs", "echo",
        "enable", "eval", "exec", "exit", "export", "fc", "fg",
        "getopts", "hash", "help", "history", "jobs", "kill", "let",
        "local", "logout", "mapfile", "popd", "printf", "pushd",
        "pwd", "read", "readonly", "return", "set", "shift", "shopt",
        "source", "suspend", "test", "times", "trap", "type", "typeset",
        "ulimit", "umask", "unalias", "unset", "wait",
        "if", "then", "else", "elif", "fi", "for", "while", "until",
        "case", "esac", "select", "function", "time", "coproc"
    })
    return sorted(candidates)


def _unknown_command(command_name, candidates):
    _clear()
    print(CYAN + UNKNOWN_ART + RESET)
    print()
    print("  Comando não reconhecido: " + command_name)
    suggestions = difflib.get_close_matches(
        command_name, candidates, n=5, cutoff=0.48
    )
    if suggestions:
        print("\n  Talvez você quisesse digitar:")
        for suggestion in suggestions:
            print("    • " + suggestion)
    else:
        print("\n  Não encontrei sugestões parecidas.")
    print("\n  Digite um comando válido ou 'voltar' para sair do Nexus Terminal.")


def _change_directory(parts, current_dir, previous_dir):
    if len(parts) > 2:
        print("Uso: cd [diretório]")
        return current_dir, previous_dir

    if len(parts) == 1:
        target = Path.home()
    elif parts[1] == "-":
        if previous_dir is None:
            print("Não existe um diretório anterior.")
            return current_dir, previous_dir
        target = previous_dir
    else:
        raw_target = os.path.expandvars(parts[1])
        target = Path(raw_target).expanduser()
        if not target.is_absolute():
            target = current_dir / target

    try:
        target = target.resolve(strict=True)
        if not target.is_dir():
            print(f"Não é um diretório: {target}")
            return current_dir, previous_dir
    except OSError as error:
        print(f"Não foi possível acessar o diretório: {error}")
        return current_dir, previous_dir

    return target, current_dir


def _is_known_command(name, candidates):
    if name in candidates:
        return True
    # Caminhos explícitos são deixados para o shell validar no diretório atual.
    if "/" in name or name.startswith("."):
        return True
    return shutil.which(name) is not None


def run(cfg=None):
    cfg = cfg or {}
    current_dir = Path.cwd().resolve()
    previous_dir = None
    candidates = _command_candidates()

    _clear()
    color = CYAN
    print(color + r"""
╔════════════════════════════════════════════════════════════╗
║                    TERMUX NEXUS  •  TERMINAL                ║
║                 COMMAND LINE ENVIRONMENT                   ║
╚════════════════════════════════════════════════════════════╝
""" + RESET)
    print(color + "  " + str(cfg.get("banner", "COOLKID") or "COOLKID")[:24] + RESET)
    print(DIM + "  Digite 'voltar' para retornar ao menu principal." + RESET)
    print()

    while True:
        now = datetime.datetime.now().astimezone()
        timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
        try:
            raw = input(
                f"{CYAN}{timestamp}{RESET} "
                f"{DIM}{current_dir}{RESET}\n"
                f"{CYAN}❯ {RESET}"
            )
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo do Nexus Terminal.")
            return

        command = raw.strip()
        if not command:
            continue

        if command.lower() in ("voltar", "exit-nexus", ":q"):
            return

        if command == "clear":
            _clear()
            print(color + "  " + str(cfg.get("banner", "COOLKID") or "COOLKID")[:24] + RESET)
            print(DIM + "  Nexus Terminal • " + timestamp + RESET)
            continue

        try:
            parts = shlex.split(command)
        except ValueError as error:
            print(f"Entrada inválida: {error}")
            continue

        if not parts:
            continue

        # Mantém o diretório atual entre comandos, ao contrário de subprocessos separados.
        if parts[0] == "cd":
            current_dir, previous_dir = _change_directory(
                parts, current_dir, previous_dir
            )
            continue

        # Detecta comandos simples desconhecidos antes do shell exibir a mensagem padrão.
        first = parts[0]
        if "=" not in first and first != "export" and not _is_known_command(first, candidates):
            _unknown_command(first, candidates)
            continue

        try:
            result = subprocess.run(
                command,
                shell=True,
                executable=shutil.which("bash") or "/bin/sh",
                cwd=str(current_dir),
                check=False
            )
            if result.returncode == 127:
                _unknown_command(first, candidates)
        except KeyboardInterrupt:
            print("\nComando interrompido.")
        except OSError as error:
            print(f"Não foi possível executar o comando: {error}")
