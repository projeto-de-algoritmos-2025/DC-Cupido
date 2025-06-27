import random
import math

class Player:
    def __init__(self, id, name, x, y, kind="Player"):
        self.id = id
        self.name = name
        self.x = x
        self.y = y
        self.kind = kind
        self.state = "normal"
        self.proximity_counter = 0  # para detectar trapaça

    def move(self):
        dx = random.randint(-5, 5)
        dy = random.randint(-5, 5)
        self.x = max(0, min(1000, self.x + dx))
        self.y = max(0, min(1000, self.y + dy))

    def distance_to(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)

