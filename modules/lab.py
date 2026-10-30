"""NEXUS LAB — experiências visuais para o terminal."""

import os
import random
import shutil
import time


RESET = "\033[0m"
COLORS = [
    (0, 255, 255),
    (0, 210, 255),
    (70, 150, 255),
    (160, 100, 255),
    (255, 80, 220),
]


def _clear():
    os.system("clear")


def _pause():
    try:
        input("\nPressione Enter para voltar...")
    except EOFError:
        pass


def _gradient(text):
    output = []
    steps = max(1, len(text) - 1)
    for index, char in enumerate(text):
        position = index / steps
        scaled = position * (len(COLORS) - 1)
        left = int(scaled)
        right = min(left + 1, len(COLORS) - 1)
        fraction = scaled - left
        rgb = tuple(
            int(COLORS[left][channel] * (1 - fraction) +
                COLORS[right][channel] * fraction)
            for channel in range(3)
        )
        output.append(f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{char}")
    print("".join(output) + RESET)


def _banner():
    text = input("Texto do banner > ").strip()[:48]
    if not text:
        print("Texto vazio.")
        return
    width = min(max(len(text) + 4, 24), 54)
    line = "═" * width
    _gradient("╔" + line + "╗")
    _gradient("║" + text.center(width) + "║")
    _gradient("╚" + line + "╝")


def _gradient_text():
    text = input("Texto para colorir > ")
    if text:
        _gradient(text)


def _animation():
    frames = ("[    ]", "[=   ]", "[==  ]", "[=== ]", "[====]")
    print("Executando demonstração de animação...")
    for cycle in range(3):
        for frame in frames:
            print("\r" + frame + "  NEXUS LAB", end="", flush=True)
            time.sleep(0.12)
    print("\nConcluído!")


def _ascii_art():
    print(" [1] NEXUS")
    print(" [2] Estrela")
    print(" [3] Caixa")
    choice = input("Modelo > ").strip()
    art = {
        "1": r"""
 _   _ _____  ___  _   _ ____
| \ | | ____|/ _ \| | | / ___|
|  \| |  _| | | | | | | \___ \
| |\  | |___| |_| | |_| |___) |
|_| \_|_____|\__\_\\___/|____/
""",
        "2": r"""
       /\
      /  \
  ___/ /\ \___
  \   /  \   /
   \ /____\ /
    \      /
     \____/
""",
        "3": r"""
╔══════════════════╗
║   TERMUX NEXUS   ║
║   SYSTEM READY   ║
╚══════════════════╝
"""
    }.get(choice)
    if art:
        _gradient(art.rstrip("\n"))
    else:
        print("Modelo inválido.")


def run(cfg=None):
    while True:
        _clear()
        _gradient("╔══════════════════════════════════════════════╗")
        _gradient("║                  NEXUS LAB                   ║")
        _gradient("║             TERMINAL EXPERIMENTS             ║")
        _gradient("╚══════════════════════════════════════════════╝")
        print("\n [1] Criar banner personalizado")
        print(" [2] Gerar texto com gradiente ANSI")
        print(" [3] Animação de carregamento")
        print(" [4] Arte ASCII")
        print(" [5] Efeito de caracteres aleatórios")
        print(" [0] Voltar")
        choice = input("\nLab > ").strip()

        if choice == "1":
            _clear()
            _banner()
            _pause()
        elif choice == "2":
            _clear()
            _gradient_text()
            _pause()
        elif choice == "3":
            _clear()
            _animation()
            _pause()
        elif choice == "4":
            _clear()
            _ascii_art()
            _pause()
        elif choice == "5":
            _clear()
            width = min(shutil.get_terminal_size((60, 20)).columns, 80)
            for _ in range(8):
                print("".join(random.choice("01░▒▓<>/\\") for _ in range(width)))
                time.sleep(0.08)
            _pause()
        elif choice == "0":
            return
