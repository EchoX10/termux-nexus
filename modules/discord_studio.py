"""NEXUS Discord Bot Studio: construtor guiado de bots sem escrever código."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlencode

import getpass

ROOT = Path.home() / "NexusDiscordBots"
RESET = "\033[0m"
CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
RED = "\033[91m"


TEMPLATES = [
    ("community", "Comunidade", "Boas-vindas, despedidas e comandos úteis"),
    ("moderation", "Moderação", "Comandos de moderação e utilidades"),
    ("support", "Suporte", "Base para atendimento e tickets"),
    ("custom", "Personalizado", "Escolha exatamente os recursos"),
]


def _ask(title, text, default=""):
    print("\\n" + CYAN + title + RESET)
    print(text)
    suffix = f" [{default}]" if default else ""
    try:
        value = input("> " + suffix + " ").strip()
    except (EOFError, KeyboardInterrupt):
        return None
    return value if value else (default if default else "")


def _choose(title, text, choices):
    print("\\n" + CYAN + title + RESET)
    print(text)
    for index, item in enumerate(choices, 1):
        label = item[1] if len(item) > 1 else str(item[0])
        print(f"  [{index}] {label}")
    print("  [0] Voltar")
    try:
        answer = input("\\nEscolha uma opção: ").strip()
    except (EOFError, KeyboardInterrupt):
        return None
    if not answer.isdigit():
        print("Opção inválida.")
        return None
    number = int(answer)
    if number == 0 or number > len(choices):
        return None
    return choices[number - 1][0]


def _checks(title, text, choices):
    selected = []
    while True:
        print("\\n" + CYAN + title + RESET)
        print(text)
        for index, item in enumerate(choices, 1):
            mark = "X" if item[0] in selected else " "
            print(f"  [{mark}] {index}. {item[1]}")
        print("  [D] Concluir seleção")
        try:
            answer = input("Digite o número para alternar: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return selected
        if answer == "d":
            return selected
        if answer.isdigit() and 1 <= int(answer) <= len(choices):
            key = choices[int(answer) - 1][0]
            if key in selected:
                selected.remove(key)
            else:
                selected.append(key)


def _confirm(title, text):
    print("\\n" + CYAN + title + RESET)
    print(text)
    try:
        return input("[s/N] > ").strip().lower() in ("s", "sim")
    except (EOFError, KeyboardInterrupt):
        return False


def _notice(title, text):
    print("\\n" + CYAN + title + RESET)
    print(text)
    try:
        input("\\nPressione Enter para continuar...")
    except (EOFError, KeyboardInterrupt):
        pass


def _secret(title, text):
    print("\\n" + CYAN + title + RESET)
    print(text)
    try:
        return getpass.getpass("Token (entrada oculta): ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""

ROOT = Path.home() / "NexusDiscordBots"
RESET = "\033[0m"
CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
RED = "\033[91m"

TEMPLATES = [
    ("community", "Comunidade", "Boas-vindas, despedidas e comandos úteis"),
    ("moderation", "Moderação", "Comandos de moderação e utilidades"),
    ("support", "Suporte", "Base para atendimento e tickets"),
    ("custom", "Personalizado", "Escolha exatamente os recursos"),
]


def _dialogs():
    if input_dialog is None:
        print("O Prompt Toolkit não está instalado. Execute novamente o instalador do Nexus.")
        return False
    return True


def _ask(title, text, default=""):
    result = input_dialog(title=title, text=text, default=default).run()
    return None if result is None else str(result).strip()


def _choose(title, text, choices):
    return radiolist_dialog(title=title, text=text, values=choices).run()


def _checks(title, text, choices):
    result = checkboxlist_dialog(title=title, text=text, values=choices).run()
    return result or []


def _confirm(title, text):
    return yes_no_dialog(title=title, text=text).run() is True


def _notice(title, text):
    message_dialog(title=title, text=text).run()


def _slug(value):
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip()).strip("-_").lower()
    return value[:32] or "meu-bot"


def _load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def _projects():
    ROOT.mkdir(parents=True, exist_ok=True)
    return sorted(p for p in ROOT.iterdir() if p.is_dir() and (p / "bot.json").is_file())


def _bot_source(config):
    custom = config.get("commands", [])
    command_defs = []
    for item in custom:
        name = re.sub(r"[^a-z0-9_]", "", item.get("name", "").lower())[:32]
        response = item.get("response", "").replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
        if name and response:
            command_defs.append(
                "@tree.command(name=" + repr(name) + ", description=" + repr(("Resposta personalizada: " + name)[:100]) + ")\n"
                "async def custom_" + name + "(interaction: discord.Interaction):\n"
                "    await interaction.response.send_message(" + repr(response) + ", ephemeral=False)\n"
            )

    welcome_block = ""
    if config.get("welcome") or config.get("goodbye"):
        welcome_block = """
@client.event
async def on_member_join(member):
    channel_id = SETTINGS.get("welcome_channel_id")
    if SETTINGS.get("welcome") and channel_id:
        channel = member.guild.get_channel(int(channel_id))
        if channel:
            text = SETTINGS.get("welcome_text", "Bem-vindo(a), {user}!")
            await channel.send(text.replace("{user}", member.mention).replace("{server}", member.guild.name))

@client.event
async def on_member_remove(member):
    channel_id = SETTINGS.get("welcome_channel_id")
    if SETTINGS.get("goodbye") and channel_id:
        channel = member.guild.get_channel(int(channel_id))
        if channel:
            text = SETTINGS.get("goodbye_text", "{user} saiu do servidor.")
            await channel.send(text.replace("{user}", member.display_name).replace("{server}", member.guild.name))
"""

    ticket_block = ""
    if config.get("tickets"):
        ticket_block = """
@tree.command(name="ticket", description="Abre um canal privado de atendimento")
async def ticket(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("Use este comando dentro de um servidor.", ephemeral=True)
        return
    guild = interaction.guild
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True),
    }
    safe_name = "ticket-" + re.sub(r"[^a-z0-9-]", "", interaction.user.name.lower())[:20]
    channel = await guild.create_text_channel(safe_name or "ticket", overwrites=overwrites, reason="Ticket solicitado pelo membro")
    await channel.send(f"Atendimento aberto por {interaction.user.mention}. A equipe pode acessar este canal conforme as permissões do servidor.")
    await interaction.response.send_message(f"Seu ticket foi criado: {channel.mention}", ephemeral=True)
"""

    moderation_block = ""
    if config.get("moderation"):
        moderation_block = """
@tree.command(name="limpar", description="Apaga mensagens recentes deste canal")
@app_commands.describe(quantidade="Quantidade de mensagens (1 a 50)")
@app_commands.checks.has_permissions(manage_messages=True)
async def limpar(interaction: discord.Interaction, quantidade: app_commands.Range[int, 1, 50]):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=quantidade)
    await interaction.followup.send(f"{len(deleted)} mensagens removidas.", ephemeral=True)

@limpar.error
async def limpar_error(interaction: discord.Interaction, error):
    message = "Você precisa da permissão Gerenciar mensagens." if isinstance(error, app_commands.MissingPermissions) else "Não consegui executar essa ação."
    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)
"""

    return '''# Gerado pelo NEXUS Discord Bot Studio
import json
import os
import re
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
with open("bot.json", "r", encoding="utf-8") as file:
    SETTINGS = json.load(file)

intents = discord.Intents.default()
intents.members = bool(SETTINGS.get("welcome") or SETTINGS.get("goodbye"))
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name="ping", description="Verifica a latência do bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(client.latency * 1000)} ms")

@tree.command(name="ajuda", description="Mostra os comandos disponíveis")
async def ajuda(interaction: discord.Interaction):
    items = ["/ping", "/ajuda"]
    if SETTINGS.get("moderation"):
        items.append("/limpar (requer Gerenciar mensagens)")
    if SETTINGS.get("tickets"):
        items.append("/ticket (abre canal privado)")
    items.extend("/" + item.get("name", "") for item in SETTINGS.get("commands", []))
    await interaction.response.send_message("Comandos: " + ", ".join(items), ephemeral=True)

''' + moderation_block + "\n" + ticket_block + "\n" + welcome_block + "\n" + "".join(command_defs) + '''
@client.event
async def on_ready():
    await tree.sync()
    print(f"NEXUS conectado como {client.user}!")
    print("Use Ctrl+C para parar o bot.")

if not TOKEN:
    raise SystemExit("Token ausente. Configure DISCORD_BOT_TOKEN no arquivo .env.")
client.run(TOKEN)
'''


def _write_project(folder, config):
    folder.mkdir(parents=True, exist_ok=True)
    _save(folder / "bot.json", config)
    (folder / "bot.py").write_text(_bot_source(config), encoding="utf-8")
    (folder / "requirements.txt").write_text("discord.py>=2.4,<3\npython-dotenv>=1.0,<2\n", encoding="utf-8")
    env_file = folder / ".env"
    if not env_file.exists():
        env_file.write_text("# Token do bot; mantenha este arquivo privado.\nDISCORD_BOT_TOKEN=\n", encoding="utf-8")
    try:
        env_file.chmod(0o600)
    except OSError:
        pass
    (folder / ".gitignore").write_text(".env\n__pycache__/\n*.pyc\n", encoding="utf-8")


def _create_bot():
    name = _ask("Novo bot", "Como o bot vai se chamar?")
    if not name:
        return
    slug = _slug(name)
    if (ROOT / slug).exists():
        _notice("Nome já utilizado", "Já existe um projeto com esse nome. Escolha outro.")
        return
    template = _choose("Modelo inicial", "Escolha uma base para o seu bot:", TEMPLATES)
    if not template:
        return
    features = {
        "welcome": template == "community",
        "goodbye": template == "community",
        "moderation": template == "moderation",
        "tickets": template == "support",
    }
    if template == "custom":
        selected = _checks("Recursos", "Marque os recursos que deseja ativar:", [
            ("welcome", "Mensagem de boas-vindas"),
            ("goodbye", "Mensagem de despedida"),
            ("moderation", "Comando de moderação /limpar"),
        ])
        features = {key: key in selected for key in ("welcome", "goodbye", "moderation")}
        features["tickets"] = False
    config = {
        "name": name[:64],
        "template": template,
        "welcome": features["welcome"],
        "goodbye": features["goodbye"],
        "moderation": features["moderation"],
        "tickets": features["tickets"],
        "welcome_channel_id": "",
        "welcome_text": "Olá {user}! Seja bem-vindo(a) ao {server}!",
        "goodbye_text": "{user} saiu do {server}. Até mais!",
        "client_id": "",
        "commands": [],
    }
    folder = ROOT / slug
    _write_project(folder, config)
    _notice("Projeto criado!", f"{name} foi criado em:\n{folder}\n\nPróximo passo: abra Configurar bot para adicionar o token e o ID da aplicação.")
    

def _select_bot():
    projects = _projects()
    if not projects:
        _notice("Nenhum bot", "Crie seu primeiro bot na opção Criar novo bot.")
        return None
    choices = [(p.name, _load(p / "bot.json").get("name", p.name)) for p in projects]
    selected = _choose("Meus bots", "Selecione um projeto:", choices)
    return ROOT / selected if selected else None


def _configure_bot(folder):
    config_path = folder / "bot.json"
    config = _load(config_path)
    while True:
        choice = _choose(
            config.get("name", folder.name),
            "Escolha o que deseja configurar:",
            [
                ("identity", "ID da aplicação / Client ID"),
                ("token", "Token privado do bot"),
                ("welcome_channel", "ID do canal de boas-vindas"),
                ("welcome_text", "Texto de boas-vindas"),
                ("goodbye_text", "Texto de despedida"),
                ("add_command", "Adicionar comando personalizado"),
                ("remove_command", "Remover comando personalizado"),
                ("invite", "Gerar link de convite"),
                ("save", "Salvar e gerar arquivos"),
                ("back", "Voltar"),
            ],
        )
        if choice in (None, "back"):
            return
        if choice == "identity":
            value = _ask("Client ID", "Cole o Application ID (não é o token):", config.get("client_id", ""))
            if value and value.isdigit():
                config["client_id"] = value
            elif value:
                _notice("ID inválido", "O Application ID deve conter apenas números.")
        elif choice == "token":
            token = _secret("Token privado", "Cole o token do bot. Ele será salvo somente no arquivo .env local:")
            if token:
                env_file = folder / ".env"
                old = env_file.read_text(encoding="utf-8") if env_file.exists() else ""
                lines = [line for line in old.splitlines() if not line.startswith("DISCORD_BOT_TOKEN=") and not line.startswith("# Token")]
                lines.append("DISCORD_BOT_TOKEN=" + token.strip())
                env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
                try:
                    env_file.chmod(0o600)
                except OSError:
                    pass
                _notice("Token salvo", "Token armazenado localmente. Não compartilhe o arquivo .env.")
        elif choice == "welcome_channel":
            value = _ask("Canal", "ID numérico do canal onde as mensagens serão enviadas:", config.get("welcome_channel_id", ""))
            if value == "" or value.isdigit():
                config["welcome_channel_id"] = value
            elif value:
                _notice("ID inválido", "Use o ID numérico do canal.")
        elif choice in ("welcome_text", "goodbye_text"):
            key = "welcome_text" if choice == "welcome_text" else "goodbye_text"
            value = _ask("Mensagem", "Use {user} para mencionar/nome e {server} para o servidor:", config.get(key, ""))
            if value is not None:
                config[key] = value[:1800]
        elif choice == "add_command":
            name = _ask("Novo comando", "Nome sem barra, usando letras, números ou _:") or ""
            name = re.sub(r"[^a-z0-9_]", "", name.lower())[:32]
            if not name:
                _notice("Nome inválido", "Escolha um nome simples, como regras ou redes.")
                continue
            if any(c.get("name") == name for c in config.get("commands", [])):
                _notice("Já existe", "Esse comando já está cadastrado.")
                continue
            response = _ask("Resposta do comando", "Qual mensagem o bot deve enviar?")
            if response:
                config.setdefault("commands", []).append({"name": name, "response": response[:1800]})
        elif choice == "remove_command":
            commands = config.get("commands", [])
            if not commands:
                _notice("Sem comandos", "Ainda não há comandos personalizados.")
                continue
            selected = _choose("Remover comando", "Selecione:", [(str(i), "/" + c["name"]) for i, c in enumerate(commands)])
            if selected is not None:
                commands.pop(int(selected))
        elif choice == "invite":
            _save(config_path, config)
            _write_project(folder, config)
            _invite(folder, config)
        elif choice == "save":
            _write_project(folder, config)
            _notice("Salvo", "Configurações e arquivos do bot foram atualizados.")


def _invite(folder, config):
    client_id = config.get("client_id", "")
    if not client_id:
        _notice("Falta o Client ID", "Configure o Application ID primeiro.")
        return
    permissions = 0
    if config.get("moderation"):
        permissions |= 8192
    if config.get("tickets"):
        permissions |= 16
    params = urlencode({
        "client_id": client_id,
        "scope": "bot applications.commands",
        "permissions": str(permissions),
    })
    url = "https://discord.com/oauth2/authorize?" + params
    _notice("Link de convite", "Copie este link e abra no navegador:\n\n" + url + "\n\nConfira as permissões antes de adicionar o bot.")


def _run_bot(folder):
    _write_project(folder, _load(folder / "bot.json"))
    env_file = folder / ".env"
    if not env_file.exists() or "DISCORD_BOT_TOKEN=" not in env_file.read_text(encoding="utf-8"):
        _notice("Token ausente", "Abra Configurar bot e adicione o token privado.")
        return
    if not _confirm("Iniciar bot", "O bot será iniciado no Termux. Use Ctrl+C para parar. Continuar?"):
        return
    print(CYAN + "\nNEXUS • Instalando dependências do projeto...\n" + RESET)
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=str(folder), check=True)
        subprocess.run([sys.executable, "bot.py"], cwd=str(folder), check=False)
    except subprocess.CalledProcessError as error:
        _notice("Falha", "Não foi possível instalar as dependências:\n" + str(error))


def _manage_bot():
    folder = _select_bot()
    if folder is None:
        return
    while True:
        choice = _choose(
            folder.name,
            "Gerenciar projeto:",
            [
                ("configure", "Configurar bot"),
                ("generate", "Gerar/atualizar arquivos"),
                ("run", "Iniciar bot"),
                ("invite", "Gerar link de convite"),
                ("back", "Voltar"),
            ],
        )
        if choice in (None, "back"):
            return
        config = _load(folder / "bot.json")
        if choice == "configure":
            _configure_bot(folder)
        elif choice == "generate":
            _write_project(folder, config)
            _notice("Arquivos atualizados", f"Arquivos gerados em:\n{folder}")
        elif choice == "run":
            _run_bot(folder)
        elif choice == "invite":
            _invite(folder, config)


def run(cfg=None):
    if not _dialogs():
        return
    ROOT.mkdir(parents=True, exist_ok=True)
    while True:
        os.system("clear")
        print(CYAN + r"""
╔══════════════════════════════════════════════════════╗
║              NEXUS DISCORD BOT STUDIO                ║
║                CONSTRUTOR VISUAL                     ║
╚══════════════════════════════════════════════════════╝
""" + RESET)
        print("  Crie e configure bots do Discord sem programar.\n")
        print("  [1] Criar novo bot")
        print("  [2] Meus bots / Gerenciar")
        print("  [3] Abrir pasta dos projetos")
        print("  [0] Voltar ao NEXUS\n")
        choice = _choose(
            "NEXUS Discord Bot Studio",
            "Digite o número da opção desejada:",
            [
                ("create", "Criar novo bot"),
                ("manage", "Meus bots / Gerenciar"),
                ("folder", "Abrir pasta dos projetos"),
                ("back", "Voltar ao NEXUS"),
            ],
        )
        if choice in (None, "back"):
            return
        if choice == "create":
            _create_bot()
        elif choice == "manage":
            _manage_bot()
        elif choice == "folder":
            subprocess.run(["termux-open", str(ROOT)], check=False)
            _notice("Pasta dos projetos", str(ROOT) + "\nSe termux-open não estiver disponível, abra esse caminho no gerenciador de arquivos.")
