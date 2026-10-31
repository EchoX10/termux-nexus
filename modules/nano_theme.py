"""Instalador seguro do tema NEXUS CYBER para GNU Nano."""

from __future__ import annotations

from pathlib import Path

HOME = Path.home()
NANO_DIR = HOME / ".config" / "nano"
THEME_FILE = NANO_DIR / "nexus.nanorc"
NANORC = HOME / ".nanorc"
INCLUDE_LINE = f'include "{THEME_FILE}"'

THEME = r"""# NEXUS CYBER — tema para GNU Nano
# Interface em ciano, azul e cores neon.

set linenumbers
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
set promptcolor brightcyan,black

# Destaque geral de código
color brightmagenta "\\<(def|class|return|if|else|elif|for|while|import|from|as|try|except|with|lambda|pass|break|continue|True|False|None)\\>"
color brightgreen "\"[^\"]*\"|'[^']*'"
color brightyellow "\\<[0-9]+\\>"
color brightblack "#.*$"
"""

def theme_status() -> bool:
    """Retorna True quando o tema está incluído no ~/.nanorc."""
    try:
        return INCLUDE_LINE in NANORC.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False


def apply_theme() -> str:
    """Instala o tema sem substituir configurações pessoais existentes."""
    NANO_DIR.mkdir(parents=True, exist_ok=True)
    THEME_FILE.write_text(THEME, encoding="utf-8")

    if NANORC.exists():
        current = NANORC.read_text(encoding="utf-8")
    else:
        current = ""

    if INCLUDE_LINE not in current.splitlines():
        separator = "" if not current or current.endswith("\n") else "\n"
        NANORC.write_text(
            current + separator + "# NEXUS CYBER Nano theme\n" + INCLUDE_LINE + "\n",
            encoding="utf-8"
        )

    return "Tema NEXUS CYBER ativado! Abra o Nano novamente para ver as mudanças."


def remove_theme() -> str:
    """Desativa somente a integração do Nexus e preserva o restante do ~/.nanorc."""
    if NANORC.exists():
        lines = NANORC.read_text(encoding="utf-8").splitlines()
        kept = []
        skip_marker = False

        for line in lines:
            if line.strip() == "# NEXUS CYBER Nano theme":
                skip_marker = True
                continue
            if line.strip() == INCLUDE_LINE:
                skip_marker = False
                continue
            kept.append(line)

        while kept and not kept[-1].strip():
            kept.pop()

        content = "\n".join(kept)
        NANORC.write_text(content + ("\n" if content else ""), encoding="utf-8")

    if THEME_FILE.exists():
        THEME_FILE.unlink()

    try:
        NANO_DIR.rmdir()
    except OSError:
        pass

    return "Tema NEXUS CYBER removido. Suas outras configurações do Nano foram preservadas."
