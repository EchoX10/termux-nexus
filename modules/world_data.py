"""Conteúdo inicial do mundo sandbox NEXUS: World of Choices."""

WORLD = {
    "crossroads": {
        "name": "Encruzilhada de Brumafria",
        "region": "Terras do Norte",
        "description": "Uma estrada antiga corta um vale coberto por capim alto. Ao longe, fumaça sobe entre as árvores.",
        "exits": {"1": "old_bridge", "2": "pine_camp"},
        "exit_labels": {"1": "Ponte de Pedra", "2": "Acampamento dos Pinheiros"},
        "discoveries": ["marco_antigo"],
        "npc": "mira",
    },
    "old_bridge": {
        "name": "Ponte de Pedra",
        "region": "Terras do Norte",
        "description": "A ponte atravessa um rio escuro. Marcas recentes aparecem entre as pedras antigas.",
        "exits": {"1": "crossroads"},
        "exit_labels": {"1": "Voltar à Encruzilhada"},
        "discoveries": ["moeda_antiga"],
        "npc": None,
    },
    "pine_camp": {
        "name": "Acampamento dos Pinheiros",
        "region": "Terras do Norte",
        "description": "Um pequeno acampamento abandonado. A fogueira ainda guarda um pouco de calor.",
        "exits": {"1": "crossroads"},
        "exit_labels": {"1": "Voltar à Encruzilhada"},
        "discoveries": ["kit_viagem"],
        "npc": "oren",
    },
}

CHARACTERS = {
    "mira": {
        "name": "Mira, a viajante",
        "dialogue": [
            "Você também ouviu o sino durante a noite?",
            "Dizem que a ponte guarda uma passagem esquecida.",
            "Se encontrar algo estranho, não entregue a qualquer pessoa.",
        ],
    },
    "oren": {
        "name": "Oren, o cartógrafo",
        "dialogue": [
            "Estou tentando atualizar este mapa há semanas.",
            "O norte muda quando a neblina chega. Pelo menos é o que dizem.",
        ],
    },
}

ITEMS = {
    "marco_antigo": {"name": "Fragmento de marco", "description": "Uma peça de pedra com um símbolo quase apagado."},
    "moeda_antiga": {"name": "Moeda antiga", "description": "Uma moeda pesada, marcada por um sol de oito pontas."},
    "kit_viagem": {"name": "Kit de viagem", "description": "Um pequeno conjunto de suprimentos úteis."},
}
