"""NEXUS Themes — paletas completas para a interface do Nexus."""
THEMES = {
    "cyber":   {"label":"NEXUS CYBER", "ansi":"\033[96m", "hex":"#00e5ff", "bg":"#07131a"},
    "matrix":  {"label":"MATRIX",      "ansi":"\033[92m", "hex":"#39ff14", "bg":"#020a04"},
    "minimal": {"label":"MINIMAL",    "ansi":"\033[97m", "hex":"#d6d6d6", "bg":"#111111"},
    "bl5ck":   {"label":"BL5CK",      "ansi":"\033[95m", "hex":"#b56cff", "bg":"#100818"},
}
def apply_theme(cfg, name):
    if name not in THEMES:
        return False
    cfg["theme"] = name
    return True
def run(cfg, save_config):
    import os
    while True:
        os.system("clear")
        active = cfg.get("theme", "cyber")
        print("\033[96mNEXUS THEMES\033[0m\n")
        for key, theme in THEMES.items():
            mark = "  < ATIVO" if key == active else ""
            print(f"[{key}] {theme['label']}{mark}")
        print("\n[0] Voltar")
        choice = input("\nNexus/themes > ").strip().lower()
        if choice == "0":
            return
        if apply_theme(cfg, choice):
            save_config(cfg)
            print(f"Tema {THEMES[choice]['label']} aplicado!")
            input("\nEnter para continuar...")
        else:
            print("Tema não reconhecido.")
            input("\nEnter para continuar...")
