"""Animações leves para o terminal, sem dependências externas."""

from __future__ import annotations

import shutil
import sys
import time

CYAN = "\033[38;2;75;210;235m"
BLUE = "\033[38;2;85;125;220m"
DIM = "\033[2m"
RESET = "\033[0m"


def clear() -> None:
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def typewriter(text: str, delay: float = 0.018) -> None:
    """Escreve texto com ritmo constante; Ctrl+C interrompe a animação."""
    start = time.monotonic()
    for index, char in enumerate(text):
        sys.stdout.write(char)
        if char == "\n":
            sys.stdout.flush()
            continue
        target = start + (index + 1) * delay
        remaining = target - time.monotonic()
        if remaining > 0:
            time.sleep(remaining)
    sys.stdout.flush()


def transition(label: str = "EXPLORANDO", duration: float = 0.42) -> None:
    width = max(16, min(shutil.get_terminal_size((80, 24)).columns - 4, 54))
    frames = ("·", "••", "•••", "••", "·")
    start = time.monotonic()
    frame = 0
    while time.monotonic() - start < duration:
        dots = frames[frame % len(frames)]
        sys.stdout.write(f"\r{BLUE}{label}{dots:<3}{RESET}")
        sys.stdout.flush()
        frame += 1
        time.sleep(0.075)
    sys.stdout.write("\r" + " " * width + "\r")
    sys.stdout.flush()


def title() -> None:
    print(CYAN + "╔══════════════════════════════════════╗")
    print("║       N E X U S  •  W O R L D       ║")
    print("║            OF CHOICES                ║")
    print("╚══════════════════════════════════════╝" + RESET)
