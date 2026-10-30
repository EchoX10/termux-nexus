#!/data/data/com.termux/files/usr/bin/bash
set -eu
ROOT="$(cd "$(dirname "$0")" && pwd)"
PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
BIN="$PREFIX/bin"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/termux-nexus"
mkdir -p "$BIN" "$CONFIG"
if ! command -v python >/dev/null 2>&1; then
  echo "Python não está instalado. Execute: pkg install python"
  exit 1
fi
cp "$ROOT/main.py" "$BIN/termux-nexus"
chmod 755 "$BIN/termux-nexus"
if [ ! -f "$CONFIG/config.json" ]; then
  printf '%s\n' '{"theme":"cyan","banner":"COOLKID","show_clock":true}' > "$CONFIG/config.json"
fi
touch "$CONFIG/enabled"
INTEGRATION="$ROOT/shell-integration.sh"
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
  if [ -f "$rc" ] && ! grep -Fq "$INTEGRATION" "$rc"; then
    cp "$rc" "$rc.termux-nexus.bak"
    printf '\n# Termux Nexus\n[ -f "%s" ] && source "%s"\n' "$INTEGRATION" "$INTEGRATION" >> "$rc"
  fi
done
# Make sure the current interactive shell's usual startup file is present.
if [ -n "${ZSH_VERSION:-}" ] && [ ! -f "$HOME/.zshrc" ]; then
  printf '[ -f "%s" ] && source "%s"\n' "$INTEGRATION" "$INTEGRATION" > "$HOME/.zshrc"
elif [ ! -f "$HOME/.bashrc" ]; then
  printf '[ -f "%s" ] && source "%s"\n' "$INTEGRATION" "$INTEGRATION" > "$HOME/.bashrc"
fi
echo
echo "Termux Nexus instalado com sucesso."
echo "Comandos disponíveis: nexus, nexusconfig, nexusexit"
echo "Abra uma nova sessão para testar o banner automático."
