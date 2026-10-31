"""Configuração do tema NEXUS CYBER para GNU Nano.

As opções 'set' ficam diretamente em ~/.nanorc, como o Nano exige.
O realce de sintaxe continua usando as definições nativas do Nano.
"""
from __future__ import annotations
from pathlib import Path

HOME = Path.home()
NANO_DIR = HOME / ".config" / "nano"
THEME_FILE = NANO_DIR / "nexus.nanorc"
NANORC = HOME / ".nanorc"
OPTIONS_MARKER = "# NEXUS CYBER Nano options"
OPTIONS = """set linenumbers
set mouse
set constantshow
set softwrap
set tabsize 4
set tabstospaces
set titlecolor brightwhite,blue
set statuscolor brightwhite,brightcyan
set numbercolor brightcyan,black
set keycolor brightcyan
set functioncolor brightyellow
set selectedcolor brightwhite,brightblue
set errorcolor brightwhite,red
set promptcolor brightcyan,black"""

def _read() -> str:
    try:
        return NANORC.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""

def _without_nexus(content: str) -> str:
    result = []
    removing = False
    for line in content.splitlines():
        if line.strip() == OPTIONS_MARKER:
            removing = True
            continue
        if removing and line.startswith("set "):
            continue
        if removing:
            removing = False
        result.append(line)
    return "\n".join(result).rstrip()

def theme_status() -> bool:
    lines = _read().splitlines()
    return OPTIONS_MARKER in lines and "set linenumbers" in lines

def apply_theme() -> str:
    current = _without_nexus(_read())
    block = OPTIONS_MARKER + "\n" + OPTIONS
    NANORC.parent.mkdir(parents=True, exist_ok=True)
    NANORC.write_text((current + "\n\n" if current else "") + block + "\n", encoding="utf-8")
    # Remove o arquivo de sintaxe experimental antigo, se existir.
    try:
        THEME_FILE.unlink()
        NANO_DIR.rmdir()
    except OSError:
        pass
    return "Tema NEXUS CYBER ativado. As opções foram aplicadas diretamente em ~/.nanorc."

def remove_theme() -> str:
    current = _without_nexus(_read())
    NANORC.write_text(current + ("\n" if current else ""), encoding="utf-8")
    try:
        THEME_FILE.unlink()
        NANO_DIR.rmdir()
    except OSError:
        pass
    return "Tema NEXUS CYBER removido; suas outras configurações foram preservadas."
