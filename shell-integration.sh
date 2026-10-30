# Termux Nexus shell integration. Safe to source in Bash or Zsh.
_NEXUS_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/termux-nexus"
_NEXUS_BIN="${PREFIX:-/data/data/com.termux/files/usr}/bin/termux-nexus"

nexus() {
  if [ -x "$_NEXUS_BIN" ]; then
    python "$_NEXUS_BIN"
  else
    echo "Nexus não encontrado. Execute novamente install.sh."
  fi
}

nexusconfig() {
  if [ -x "$_NEXUS_BIN" ]; then
    python "$_NEXUS_BIN" config
  else
    echo "Nexus não encontrado. Execute novamente install.sh."
  fi
}

nexusexit() {
  rm -f "$_NEXUS_CONFIG/enabled"
  echo "Inicialização automática desativada. O comando nexus continua disponível."
}

_nexus_autostart() {
  case "$-" in *i*) ;; *) return ;; esac
  if [ -f "$_NEXUS_CONFIG/enabled" ] && [ -x "$_NEXUS_BIN" ]; then
    python "$_NEXUS_BIN" </dev/null 2>/dev/null || true
  fi
}
_nexus_autostart
unset -f _nexus_autostart
