"""Instalador seguro do tema NEXUS CYBER para GNU Nano."""

from __future__ import annotations

from pathlib import Path

HOME = Path.home()
NANO_DIR = HOME / ".config" / "nano"
THEME_FILE = NANO_DIR / "nexus.nanorc"
NANORC = HOME / ".nanorc"
INCLUDE_LINE = f'include "{THEME_FILE}"'
OPTIONS_MARKER = "# NEXUS CYBER Nano options"
INCLUDE_MARKER = "# NEXUS CYBER Nano theme"

# As diretivas de cor precisam estar dentro de um bloco syntax.
# O padrão genérico oferece realce básico em arquivos sem uma sintaxe específica.
THEME = r"""# NEXUS CYBER — cores para GNU Nano
syntax "nexus" ""
color brightmagenta "\\<(def|class|return|if|else|elif|for|while|import|from|as|try|except|with|lambda|pass|break|continue|True|False|None)\\>"
color brightgreen "\"[^\"]*\"|'[^']*'"
color brightyellow "\\<[0-9]+\\>"
color brightblack "#.*$"
"""

OPTIONS = """# NEXUS CYBER Nano options
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
"""


def _read_nanorc() -> str:
    try:
        return NANORC.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _remove_managed_blocks(content: str) -> str:
    """Remove somente blocos gerenciados pelo Nexus, mantendo o resto intacto."""
    lines = content.splitlines()
    kept = []
    skip = False

    for line in lines:
        if line.strip() in (OPTIONS_MARKER, INCLUDE_MARKER):
            skip = True
            continue
        if skip and line.startswith("set "):
            continue
        if skip and line.strip() == INCLUDE_LINE:
            skip = False
            continue
        if skip:
            # O bloco de opções termina na primeira linha que não é uma opção.
            skip = False
        kept.append(line)

    return "\n".join(kept).rstrip()


def theme_status() -> bool:
    """Retorna True quando a integração está presente no ~/.nanorc."""
    content = _read_nanorc().splitlines()
    return OPTIONS_MARKER in content and INCLUDE_LINE in content


def apply_theme() -> str:
    """Instala o tema sem substituir configurações pessoais existentes."""
    NANO_DIR.mkdir(parents=True, exist_ok=True)
    THEME_FILE.write_text(THEME, encoding="utf-8")

    current = _remove_managed_blocks(_read_nanorc())
    blocks = [part for part in (current, OPTIONS.rstrip(), INCLUDE_MARKER + "\n" + INCLUDE_LINE) if part]
    NANORC.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")

    return "Tema NEXUS CYBER corrigido e ativado! Feche e abra o Nano novamente."


def remove_theme() -> str:
    """Remove apenas as configurações adicionadas pelo Nexus."""
    current = _remove_managed_blocks(_read_nanorc())
    NANORC.write_text(current + ("\n" if current else ""), encoding="utf-8")

    if THEME_FILE.exists():
        THEME_FILE.unlink()

    try:
        NANO_DIR.rmdir()
    except OSError:
        pass

    return "Tema NEXUS CYBER removido. Suas outras configurações foram preservadas."
