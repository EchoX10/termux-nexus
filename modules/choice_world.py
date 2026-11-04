"""NEXUS: World of Choices — aventura sandbox para Termux."""

from __future__ import annotations

import random
import time

from modules.world_animation import BLUE, CYAN, DIM, RESET, clear, title, transition, typewriter
from modules.world_data import CHARACTERS, ITEMS, WORLD
from modules.world_save import delete_save, load_game, new_game, save_game


def _pause() -> None:
    input("\nPressione Enter para continuar...")


def _scene(state: dict, animate: bool = True) -> None:
    place = WORLD[state["location"]]
    clear()
    title()
    print(f"{DIM}{place['region']}  /  Dia {state['flags'].get('day', 1)}{RESET}")
    print(f"\n{CYAN}◆ {place['name']}{RESET}\n")
    text = place["description"]
    if animate:
        typewriter(text + "\n", 0.012)
    else:
        print(text)
    print(f"\n{DIM}Descobertas: {len(state['discovered'])}  •  Itens: {len(state['inventory'])}  •  Locais: {len(state['visited'])}/{len(WORLD)}{RESET}")


def _discover(state: dict) -> None:
    place = WORLD[state["location"]]
    for item_id in place["discoveries"]:
        if item_id not in state["discovered"]:
            state["discovered"].append(item_id)
            state["inventory"].append(item_id)
            item = ITEMS[item_id]
            state["journal"].append(f"Encontrou: {item['name']} — {place['name']}")
            print(f"\n{BLUE}✦ Descoberta: {item['name']}{RESET}")
            typewriter(item["description"] + "\n", 0.012)
            save_game(state)


def _travel(state: dict) -> None:
    place = WORLD[state["location"]]
    print("\nCAMINHOS DISPONÍVEIS")
    destinations = list(place["exits"].items())
    for number, destination in destinations:
        print(f"[{number}] {place['exit_labels'][number]}")
    print("[0] Cancelar")
    choice = input("\nEscolha o destino > ").strip()
    if choice == "0":
        return
    destination = place["exits"].get(choice)
    if not destination:
        print("Caminho inválido.")
        _pause()
        return
    transition("VIAJANDO")
    state["location"] = destination
    if destination not in state["visited"]:
        state["visited"].append(destination)
        state["journal"].append(f"Descobriu: {WORLD[destination]['name']}")
    state["flags"]["day"] = state["flags"].get("day", 1) + (1 if random.random() < 0.25 else 0)
    save_game(state)
    _scene(state)
    _discover(state)
    _pause()


def _talk(state: dict) -> None:
    npc_id = WORLD[state["location"]].get("npc")
    if not npc_id:
        print("\nNão há ninguém por aqui no momento.")
        _pause()
        return
    npc = CHARACTERS[npc_id]
    print(f"\n{CYAN}{npc['name']}{RESET}")
    lines = npc["dialogue"]
    for index, line in enumerate(lines, 1):
        print(f"[{index}] {line}")
    print("[0] Sair")
    choice = input("\nResponder > ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(lines):
        state["relationships"][npc_id] = state["relationships"].get(npc_id, 0) + 1
        state["flags"][f"heard_{npc_id}_{choice}"] = True
        state["journal"].append(f"Conversou com {npc['name']}.")
        save_game(state)
        print("\nA conversa ficará registrada na memória deste mundo.")
    _pause()


def _inventory(state: dict) -> None:
    print("\nINVENTÁRIO")
    if not state["inventory"]:
        print("Ainda está vazio.")
    for item_id in state["inventory"]:
        item = ITEMS[item_id]
        print(f"\n• {item['name']}\n  {item['description']}")
    _pause()


def _journal(state: dict) -> None:
    print("\nDIÁRIO DE EXPLORAÇÃO")
    for entry in state["journal"][-20:]:
        print("• " + entry)
    _pause()


def _world_map(state: dict) -> None:
    print("\nMAPA CONHECIDO")
    for place_id, place in WORLD.items():
        marker = "●" if place_id in state["visited"] else "○"
        current = "  ← você está aqui" if place_id == state["location"] else ""
        print(f"{marker} {place['name']}{current}")
    _pause()


def _new_or_load() -> dict | None:
    saved = load_game()
    clear()
    title()
    if saved:
        print("\nUma jornada salva foi encontrada.")
        print("[1] Continuar jornada")
        print("[2] Começar mundo novo (apaga o progresso anterior)")
        print("[0] Voltar")
        choice = input("\n> ").strip()
        if choice == "1":
            return saved
        if choice == "2":
            confirm = input("Apagar o progresso anterior? [s/N] > ").strip().lower()
            if confirm == "s":
                delete_save()
                return new_game()
        return None
    print("\nNenhuma jornada encontrada.")
    print("[1] Começar aventura")
    print("[0] Voltar")
    return new_game() if input("\n> ").strip() == "1" else None


def run(cfg=None) -> None:
    state = _new_or_load()
    if state is None:
        return
    save_game(state)
    _scene(state)
    _discover(state)
    _pause()

    while True:
        _scene(state, animate=False)
        print("\n[1] Explorar caminhos")
        print("[2] Conversar")
        print("[3] Inventário")
        print("[4] Mapa")
        print("[5] Diário")
        print("[6] Observar novamente")
        print("[0] Voltar ao NEXUS")
        choice = input("\nWORLD > ").strip()
        if choice == "1":
            _travel(state)
        elif choice == "2":
            _talk(state)
        elif choice == "3":
            _inventory(state)
        elif choice == "4":
            _world_map(state)
        elif choice == "5":
            _journal(state)
        elif choice == "6":
            _scene(state)
            _discover(state)
            _pause()
        elif choice == "0":
            save_game(state)
            return
        else:
            print("Opção inválida.")
            time.sleep(0.5)
