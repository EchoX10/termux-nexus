
# TERMUX NEXUS - SHELL INTEGRATION

_NEXUS_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/termux-nexus"
_NEXUS_BIN="${PREFIX:-/data/data/com.termux/files/usr}/bin/termux-nexus"

nexus() {
    python "$_NEXUS_BIN"
}

nexusconfig() {
    python "$_NEXUS_BIN" config
}

nexusexit() {
    rm -f "$_NEXUS_CONFIG/enabled"
    echo "Inicialização automática desativada."
}

# PROMPT PERSONALIZADO - BASH
if [ -n "${BASH_VERSION:-}" ]; then
    PS1='\[\e[96m\]╭─ TERMUX NEXUS\[\e[0m\]\n\[\e[90m\]│ 📁 \w\[\e[0m\]\n\[\e[96m\]╰─ ❯ \[\e[0m\]'
fi

# PROMPT PERSONALIZADO - ZSH
if [ -n "${ZSH_VERSION:-}" ]; then
    setopt PROMPT_SUBST
    PROMPT='%F{cyan}╭─ TERMUX NEXUS%f
%F{240}│ 📁 %~%f
%F{cyan}╰─ ❯ %f'
fi

# INICIALIZAÇÃO AUTOMÁTICA
_nexus_autostart() {
    case "$-" in
        *i*) ;;
        *) return ;;
    esac

    if [ -f "$_NEXUS_CONFIG/enabled" ] && [ -x "$_NEXUS_BIN" ]; then
        printf '\033[2J\033[H'
        python "$_NEXUS_BIN"
    fi
}

_nexus_autostart
unset -f _nexus_autostart
