
#!/data/data/com.termux/files/usr/bin/bash
set -eu

ROOT="$(cd "$(dirname "$0")" && pwd)"
PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
BIN="$PREFIX/bin"
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/termux-nexus"

LIB_DIR="$PREFIX/lib/termux-nexus"

mkdir -p "$BIN" "$CONFIG" "$LIB_DIR"

# Verificar Python
if ! command -v python >/dev/null 2>&1; then
    echo "Python não está instalado. Execute: pkg install python"
    exit 1
fi

# Verificar dependências
echo "Verificando dependências do Termux Nexus..."

if ! python -c "import prompt_toolkit" >/dev/null 2>&1; then
    echo "Instalando Prompt Toolkit..."
    python -m pip install prompt_toolkit
else
    echo "Prompt Toolkit já está instalado."
fi

# Instalar aplicativo
cp "$ROOT/main.py" "$BIN/termux-nexus"
rm -rf "$LIB_DIR/modules"
cp -R "$ROOT/modules" "$LIB_DIR/modules"
chmod 755 "$BIN/termux-nexus"
find "$LIB_DIR/modules" -type f -name "*.py" -exec chmod 644 {} \;

# Criar configuração padrão
if [ ! -f "$CONFIG/config.json" ]; then
    printf '%s\n' '{"theme":"cyan","banner":"COOLKID","show_clock":true}' > "$CONFIG/config.json"
fi

touch "$CONFIG/enabled"

# Integrar com Bash e Zsh
INTEGRATION="$ROOT/shell-integration.sh"

for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$rc" ] && ! grep -Fq "$INTEGRATION" "$rc"; then
        cp "$rc" "$rc.termux-nexus.bak"
        printf '\n# Termux Nexus\n[ -f "%s" ] && source "%s"\n' "$INTEGRATION" "$INTEGRATION" >> "$rc"
    fi
done

# Criar arquivo de inicialização quando necessário
if [ -n "${ZSH_VERSION:-}" ] && [ ! -f "$HOME/.zshrc" ]; then
    printf '[ -f "%s" ] && source "%s"\n' "$INTEGRATION" "$INTEGRATION" > "$HOME/.zshrc"
elif [ ! -f "$HOME/.bashrc" ]; then
    printf '[ -f "%s" ] && source "%s"\n' "$INTEGRATION" "$INTEGRATION" > "$HOME/.bashrc"
fi

echo
echo "Termux Nexus instalado com sucesso."
echo "Comandos disponíveis: nexus, nexusconfig, nexusexit"
echo "Abra uma nova sessão para testar o banner automático."
