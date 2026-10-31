"""NEXUS Logs — histórico local de atividades do Termux Nexus."""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
import os

HOME = Path.home()
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config")) / "termux-nexus"
LOG_FILE = CONFIG_DIR / "nexus.log"
MAX_LOG_BYTES = 512 * 1024

def log_event(message: str, level: str = "INFO") -> None:
    """Registra uma linha no histórico local; nunca interrompe o programa."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if LOG_FILE.exists() and LOG_FILE.stat().st_size > MAX_LOG_BYTES:
            backup = LOG_FILE.with_suffix(".log.1")
            if backup.exists():
                backup.unlink()
            LOG_FILE.replace(backup)
        clean = " ".join(str(message).replace("\n", " ").split())[:500]
        stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
        with LOG_FILE.open("a", encoding="utf-8") as stream:
            stream.write(f"[{stamp}] [{level.upper()}] {clean}\n")
    except OSError:
        pass

def run(cfg):
    import os
    while True:
        os.system("clear")
        print("\033[96mNEXUS LOGS\033[0m")
        print(f"Arquivo: {LOG_FILE}\n")
        print("[1] Ver últimas 100 linhas")
        print("[2] Ver histórico completo")
        print("[3] Limpar histórico")
        print("[0] Voltar")
        choice = input("\nNexus/logs > ").strip()
        if choice in ("1", "2"):
            try:
                lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
                if choice == "1":
                    lines = lines[-100:]
                print("\n".join(lines) if lines else "Ainda não há registros.")
            except FileNotFoundError:
                print("Ainda não há registros.")
            except OSError as error:
                print(f"Não foi possível ler o histórico: {error}")
            try: input("\nEnter para continuar...")
            except EOFError: pass
        elif choice == "3":
            confirm = input("Apagar o histórico local? [s/N] > ").strip().lower()
            if confirm in ("s", "sim"):
                try:
                    LOG_FILE.write_text("", encoding="utf-8")
                    log_event("Histórico limpo pelo usuário")
                    print("Histórico limpo.")
                except OSError as error:
                    print(f"Falha ao limpar: {error}")
                try: input("\nEnter para continuar...")
                except EOFError: pass
        elif choice == "0":
            return
