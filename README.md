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
- Configurações persistentes em JSON.
- Integração com Bash e Zsh.
- Informações do sistema e ferramentas básicas.
- FFmpeg Glitch Video para efeitos visuais e sonoros.
- **NEXUS RADAR:** diagnóstico de rede, DNS, ping e descoberta TCP opcional na rede local.
- **NEXUS LAB:** banners personalizados, gradientes ANSI, animações e arte ASCII.
- **NEXUS COMMAND CENTER:** terminal interno com comandos próprios, histórico persistente e ajuda integrada.
- **NEXUS TERMINAL:** modo de comandos integrado, com data, hora e diretório atual no prompt, suporte a `cd` persistente e sugestões para comandos desconhecidos.
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
