# Termux Nexus

Personalizador modular para Termux, desenvolvido em Python e shell.

## Instalação

```sh
pkg update -y
pkg install -y git python
git clone https://github.com/EchoX10/termux-nexus.git
cd termux-nexus
bash install.sh
```

## Comandos

- `nexus`: abre a central de controle.
- `nexusconfig`: abre as configurações.
- `nexusexit`: desativa a inicialização automática.

## Recursos

- Interface de terminal em ciano com banner ASCII.
- **NEXUS CYBER Nano:** tema ciano/azul para o editor Nano, com numeração de linhas e cores de interface; preserva o conteúdo pré-existente de `~/.nanorc` e usa o realce de sintaxe nativo.
- Configurações persistentes em JSON.
- Integração com Bash e Zsh.
- Informações do sistema e ferramentas básicas.
- FFmpeg Glitch Video para efeitos visuais e sonoros.
- **NEXUS RADAR:** diagnóstico de rede, DNS, ping e descoberta TCP opcional na rede local.
- **NEXUS LAB:** banners personalizados, gradientes ANSI, animações e arte ASCII.
- **NEXUS COMMAND CENTER:** terminal interno com comandos próprios, histórico persistente e ajuda integrada.
- **NEXUS TERMINAL:** modo de comandos integrado, com data, hora e diretório atual no prompt, suporte a `cd` persistente e sugestões para comandos desconhecidos.
- **NEXUS Logs:** histórico local de atividades, visualização das últimas 100 linhas ou do histórico completo e limpeza com confirmação.
- **NEXUS Editor:** editor de texto integrado com abrir/criar, inserir, editar e excluir linhas, busca, substituição e salvar como.
- **NEXUS Themes:** temas CYBER, MATRIX, MINIMAL e BL5CK aplicados à interface e ao relógio do Nexus.
- **NEXUS Discord Bot Studio:** construtor guiado no próprio Termux, com modelos, mensagens automáticas, comandos personalizados, moderação básica, tickets privados, geração de arquivos e link OAuth2 de convite. Os tokens ficam no `.env` local, fora do Git.
- Instalador com backup dos arquivos de inicialização e módulos em `$PREFIX/lib/termux-nexus/modules`.

## Comandos do Command Center

```text
help
clear
time
system
ip
dns <host>
ping <host>
ascii <texto>
history
exit
```

O Command Center não executa comandos arbitrários do shell. Isso mantém seus comandos próprios separados do terminal normal do Termux.

## Radar e privacidade

O Nexus Radar não envia dados para servidores externos. A descoberta de dispositivos testa portas TCP comuns apenas na rede local, após confirmação, e deve ser usada somente em redes próprias ou com autorização. Os resultados dependem das configurações de firewall e dos serviços ativos.

## Requisitos

Termux atualizado e Python 3. O instalador instala Prompt Toolkit para o relógio dinâmico.

## Licença

MIT. Consulte [LICENSE](LICENSE).


## NEXUS Discord Bot Studio

Abra **[8] NEXUS Discord Bot Studio** na central de controle. A navegação usa caixas de diálogo no terminal: setas, Enter, seletores e campos de texto, sem exigir que a pessoa escreva código.

Os projetos ficam em `~/NexusDiscordBots`. O Studio gera `bot.py`, `bot.json`, `requirements.txt` e `.env`. O token é salvo localmente no arquivo `.env`, com permissão restrita quando suportada; nunca publique esse arquivo nem envie o token em mensagens. O `.gitignore` do projeto exclui o segredo.

Para conectar um bot, crie uma aplicação e um bot no [Discord Developer Portal](https://discord.com/developers/applications), copie o Application ID e o token diretamente para os campos correspondentes do Studio. Ative o **Server Members Intent** no portal se usar boas-vindas/despedidas. O convite usa OAuth2 com os escopos `bot` e `applications.commands`; revise as permissões antes de adicionar ao servidor.

O comando de tickets cria um canal privado para quem abriu o atendimento e para o bot. A equipe do servidor deve receber acesso conforme as permissões e regras configuradas no próprio servidor. A função de moderação `/limpar` exige a permissão Gerenciar mensagens.

O Studio instala `discord.py` e `python-dotenv` no primeiro início do bot. O processo roda no Termux em primeiro plano; use Ctrl+C para pará-lo.
