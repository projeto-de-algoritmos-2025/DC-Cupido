import random
import math
import matplotlib.pyplot as plt
import time

# --- Constantes da Simulação ---
NUM_PLAYERS = 50
NUM_TURNS = 50
SLEEP_TIME = 0.2
CHEAT_THRESHOLD = 5

# --- Constantes do Jogo ---
INTERACTION_RADIUS = 50  # Raio para iniciar interações
BATTLE_RADIUS = 15       # Raio para iniciar uma batalha
COOPERATE_RADIUS = 30    # Raio para iniciar cooperação

class Player:
    def __init__(self, id, name, x, y):
        self.id = id
        self.name = name
        self.x = x
        self.y = y
        self.kind = "Player"
        
        # Atributos de Jogo e Estado
        self.max_hp = 100
        self.hp = self.max_hp
        self.attack_power = 10
        self.state = "normal"  # normal, battle, cooperate, suspect, defeated
        self.target = None
        self.partner = None
        self.proximity_counter = {} # Dicionário para rastrear proximidade com outros jogadores

    def move(self):
        # O movimento agora depende do estado do jogador
        if self.state == "battle" and self.target:
            # Persegue o alvo
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = self.distance_to(self.target)
            if dist > 0:
                self.x += dx / dist * 3 # Movimento mais rápido em batalha
                self.y += dy / dist * 3
        elif self.state == "normal":
            # Movimento aleatório
            dx = random.randint(-5, 5)
            dy = random.randint(-5, 5)
            self.x += dx
            self.y += dy
        
        # Mantém os jogadores dentro dos limites do mapa
        self.x = max(0, min(1000, self.x))
        self.y = max(0, min(1000, self.y))

    def distance_to(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.state = "defeated"
            print(f"☠️  {self.name} foi derrotado!")

    def reset_turn_state(self):
        # Reseta estados que não são persistentes
        if self.state not in ["battle", "defeated", "suspect"]:
            self.state = "normal"
            self.partner = None
        # Se o alvo for derrotado ou fugir, sai da batalha
        if self.state == "battle" and (self.target.state == "defeated" or self.distance_to(self.target) > BATTLE_RADIUS * 2):
            self.state = "normal"
            self.target = None

    def is_available(self):
        """Verifica se o jogador pode entrar em uma nova interação."""
        return self.state == "normal"


def plot_players(players, turn):
    plt.figure(figsize=(10,10))
    
    # Filtra jogadores derrotados para não plotá-los
    active_players = [p for p in players if p.state != "defeated"]
    
    xs = [p.x for p in active_players]
    ys = [p.y for p in active_players]

    colors = []
    for p in active_players:
        if p.state == "battle": colors.append("red")
        elif p.state == "cooperate": colors.append("green")
        elif p.state == "suspect": colors.append("orange")
        else: colors.append("blue")

    plt.scatter(xs, ys, c=colors, s=60, alpha=0.8)
    
    # Desenha linhas para interações
    for p in active_players:
        if p.state == "battle" and p.target:
            plt.plot([p.x, p.target.x], [p.y, p.target.y], 'r-', lw=1.5)
        elif p.state == "cooperate" and p.partner:
            # Garante que a linha seja desenhada apenas uma vez
            if p.id < p.partner.id:
                plt.plot([p.x, p.partner.x], [p.y, p.partner.y], 'g--', lw=1)

    plt.title(f"Turno {turn} | Jogadores Ativos: {len(active_players)}/{NUM_PLAYERS}")
    plt.xlim(0, 1000)
    plt.ylim(0, 1000)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.show()

# --- Setup da Simulação ---
players = [Player(i, f"Player_{i}", random.randint(0, 1000), random.randint(0, 1000)) for i in range(NUM_PLAYERS)]
proximity_history = {}

# --- Laço Principal da Simulação ---
for turn in range(1, NUM_TURNS + 1):
    print(f"\n{'='*10} Turno {turn} {'='*10}")

    # 1. Fase de Ações e Atualizações
    # Primeiro, todos os jogadores que estão em batalha atacam
    players_in_battle = [p for p in players if p.state == "battle" and p.target]
    for p in players_in_battle:
        if p.target.state == "battle": # Garante que o alvo ainda está na batalha
            print(f"⚔️  {p.name} ataca {p.target.name}!")
            p.target.take_damage(p.attack_power)

    # 2. Fase de Movimento
    for p in players:
        if p.state != "defeated":
            p.move()

    # 3. Reset do Estado Temporário
    for p in players:
        p.reset_turn_state()

    # 4. Fase de Novas Interações (Batalha, Cooperação, etc.)
    # Usamos uma lista de IDs para não processar um jogador duas vezes no mesmo turno
    processed_ids = set()
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            p1 = players[i]
            p2 = players[j]

            if not (p1.is_available() and p2.is_available()):
                continue

            dist = p1.distance_to(p2)

            # Eventos baseados na distância
            if dist < BATTLE_RADIUS:
                p1.state = "battle"
                p2.state = "battle"
                p1.target = p2
                p2.target = p1
                print(f"🔥 Nova batalha iniciada entre {p1.name} e {p2.name}!")
            
            elif dist < COOPERATE_RADIUS:
                p1.state = "cooperate"
                p2.state = "cooperate"
                p1.partner = p2
                p2.partner = p1
                print(f"🤝 {p1.name} e {p2.name} estão cooperando.")

            # Lógica de detecção de trapaça (agora mais robusta)
            key = tuple(sorted([p1.id, p2.id]))
            if dist < COOPERATE_RADIUS:
                proximity_history[key] = proximity_history.get(key, 0) + 1
                if proximity_history[key] >= CHEAT_THRESHOLD:
                    if p1.state != "suspect":
                       p1.state = "suspect"
                       print(f"⚠️  Comportamento suspeito detectado: {p1.name}!")
                    if p2.state != "suspect":
                       p2.state = "suspect"
                       print(f"⚠️  Comportamento suspeito detectado: {p2.name}!")
            # Não reseta o contador, permitindo que a suspeita seja construída ao longo do tempo
            # Poderíamos adicionar uma lógica para diminuir o contador se eles ficarem longe
            
    # 5. Visualização
    plot_players(players, turn)
    time.sleep(SLEEP_TIME)

print("\nSimulação finalizada.")