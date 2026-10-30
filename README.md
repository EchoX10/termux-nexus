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
- Informações do sistema e ferramentas básicas de arquivos e rede.
- Instalador com backup dos arquivos de inicialização.

## Requisitos

Termux atualizado e Python 3.

## Privacidade

O projeto não coleta nem envia dados. Revise os scripts antes de executá-los se desejar auditar o funcionamento.

## Licença

MIT. Consulte [LICENSE](LICENSE).
