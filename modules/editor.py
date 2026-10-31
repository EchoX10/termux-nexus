"""NEXUS Editor — editor de texto simples para arquivos locais."""
from __future__ import annotations
from pathlib import Path
import os

from modules.themes import THEMES
DIM="\033[90m"; RESET="\033[0m"

def _show(lines, start=0):
    for i, line in enumerate(lines, start + 1):
        print(f"{DIM}{i:4}{RESET} {line}")

def _read(path):
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    except UnicodeError:
        raise ValueError("Este arquivo não parece ser texto UTF-8.")
    except OSError as error:
        raise ValueError(str(error))

def run(cfg):
    current = None
    lines = []
    dirty = False
    while True:
        os.system("clear")
        accent = THEMES.get(cfg.get("theme"), THEMES["cyber"])["ansi"]
        print(f"{accent}╔══════════════════════════════════════╗")
        print("║             NEXUS EDITOR             ║")
        print(f"╚══════════════════════════════════════╝{RESET}")
        print(f"Arquivo: {current if current else '(nenhum)'}" + ("  [ALTERAÇÕES]" if dirty else ""))
        print("\n[1] Abrir / criar arquivo")
        print("[2] Mostrar conteúdo")
        print("[3] Inserir linha")
        print("[4] Editar linha")
        print("[5] Excluir linha")
        print("[6] Buscar texto")
        print("[7] Substituir texto")
        print("[8] Salvar")
        print("[9] Salvar como")
        print("[0] Voltar")
        choice = input("\nNexus/editor > ").strip()
        if choice == "1":
            raw = input("Caminho do arquivo > ").strip()
            if not raw: continue
            path = Path(raw).expanduser()
            try:
                lines = _read(path)
                current = path
                dirty = False
                from modules.logs import log_event
                log_event(f"Editor abriu {path}")
                print("Arquivo carregado." if path.exists() else "Novo arquivo (ainda não salvo).")
            except ValueError as error:
                print(f"Erro: {error}")
            input("\nEnter para continuar...")
        elif choice == "2":
            _show(lines)
            input("\nEnter para continuar...")
        elif choice == "3":
            raw = input("Inserir antes da linha (0 = final) > ").strip()
            try:
                pos = int(raw)
                if pos < 0 or pos > len(lines): raise ValueError
                value = input("Texto > ")
                lines.insert(pos, value)
                dirty = True
            except ValueError:
                print("Número de linha inválido.")
                input("\nEnter para continuar...")
        elif choice == "4":
            try:
                n = int(input("Número da linha > "))
                if not 1 <= n <= len(lines): raise ValueError
                print(f"Atual: {lines[n-1]}")
                lines[n-1] = input("Novo texto > ")
                dirty = True
            except ValueError:
                print("Linha inválida.")
                input("\nEnter para continuar...")
        elif choice == "5":
            try:
                n = int(input("Número da linha > "))
                if not 1 <= n <= len(lines): raise ValueError
                del lines[n-1]
                dirty = True
            except ValueError:
                print("Linha inválida.")
                input("\nEnter para continuar...")
        elif choice == "6":
            term = input("Buscar > ")
            matches = [(i, line) for i, line in enumerate(lines, 1) if term and term.casefold() in line.casefold()]
            for i, line in matches: print(f"{i:4} | {line}")
            print(f"\n{len(matches)} resultado(s).")
            input("\nEnter para continuar...")
        elif choice == "7":
            old = input("Texto a substituir > ")
            if not old:
                print("O texto de busca não pode ficar vazio.")
            else:
                new = input("Substituir por > ")
                count = sum(line.count(old) for line in lines)
                lines = [line.replace(old, new) for line in lines]
                dirty = dirty or count > 0
                print(f"{count} ocorrência(s) substituída(s).")
            input("\nEnter para continuar...")
        elif choice in ("8", "9"):
            if choice == "9" or current is None:
                raw = input("Salvar em > ").strip()
                if not raw: continue
                target = Path(raw).expanduser()
            else:
                target = current
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                data = "\n".join(lines)
                if lines: data += "\n"
                target.write_text(data, encoding="utf-8")
                current = target
                dirty = False
                from modules.logs import log_event
                log_event(f"Editor salvou {target}")
                print(f"Salvo: {target}")
            except OSError as error:
                print(f"Não foi possível salvar: {error}")
            input("\nEnter para continuar...")
        elif choice == "0":
            if dirty:
                answer = input("Há alterações não salvas. Sair mesmo assim? [s/N] > ").strip().lower()
                if answer not in ("s", "sim"): continue
            return
