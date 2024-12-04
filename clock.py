from datetime import datetime
from js import document, setInterval
from pyodide import create_proxy
from js import console
from collections import deque
from dataclasses import dataclass
import random


KEY_LEFT  = 37
KEY_UP    = 38
KEY_RIGHT = 39
KEY_DOWN  = 40
KEY_W     = 87
KEY_A     = 65
KEY_S     = 83
KEY_D     = 68
KEY_R     = 82


FPS = 8
CELL = 40
SIZE = CELL - 2
LEN_X = 15
LEN_Y = 15
WIDTH = LEN_X * CELL
HEIGHT = LEN_Y * CELL
SNAKE_COLOR = "0, 255, 0"
CROSS_COLOR = "255, 255, 0"
APPLE_COLOR = "255, 0, 0"

canvas = document.getElementById("board")
canvas.width = WIDTH
canvas.height = HEIGHT
ctx = canvas.getContext("2d")


@dataclass
class Vector:
    x: int
    y: int

    def copy(self):
        return Vector(self.x, self.y)


CENTER = Vector(LEN_X // 2, LEN_Y // 2)


class Game:
    def __init__(self):
        self.dx: int = 0
        self.dy: int = 0
        self.positions = deque([CENTER])
        self.snake = [False] * (LEN_X * LEN_Y)
        self.set_snake(CENTER, True)
        self.apple = self.next_apple()
        assert(self.apple is not None)
        self.end = None

    def is_snake(self, x, y):
        return self.snake[y * LEN_X + x]

    def set_snake(self, vec: Vector, val):
        self.snake[vec.y * LEN_X + vec.x] = val

    def next_apple(self):
        x_r = random.randint(0, LEN_X - 1)
        y_r = random.randint(0, LEN_Y - 1)
        if not self.is_snake(x_r, y_r):
            return Vector(x_r, y_r)

        for x in range(x_r, LEN_X):
            for y in range(y_r, LEN_Y):
                if not self.is_snake(x, y):
                    return Vector(x, y)

        for x in range(LEN_X):
            for y in range(y_r):
                if not self.is_snake(x, y):
                    return Vector(x, y)

        for x in range(x_r):
            for y in range(y_r, LEN_Y):
                if not self.is_snake(x, y):
                    return Vector(x, y)

        return None


game = Game()


def on_key(e):
    if e.repeat: return

    if (e.keyCode == KEY_LEFT) or (e.keyCode == KEY_D):
        game.dx = -1
        game.dy = 0
    if (e.keyCode == KEY_RIGHT) or (e.keyCode == KEY_A):
        game.dx = 1
        game.dy = 0

    if (e.keyCode == KEY_UP) or (e.keyCode == KEY_W):
        game.dx = 0
        game.dy = -1
    if (e.keyCode == KEY_DOWN) or (e.keyCode == KEY_S):
        game.dx = 0
        game.dy = 1

    if e.keyCode == KEY_R:
        game.ate = True




def loop():
    if game.end is not None:
        return

    ctx.clearRect(0, 0, WIDTH, HEIGHT)
    ctx.beginPath()

    dx, dy = game.dx, game.dy
    head = game.positions[0].copy()
    game.positions.appendleft(head)
    head.x = (head.x + dx) % LEN_X
    head.y = (head.y + dy) % LEN_Y
    game.set_snake(head, True)

    if head != game.apple:
        rem = game.positions.pop()
        game.set_snake(rem, False)
    else:
        game.apple = game.next_apple()

    if game.apple is None:
        game.end = ":)"
    else:
        ctx.fillStyle = f"rgba({APPLE_COLOR})"
        ctx.fillRect(game.apple.x * CELL, game.apple.y * CELL, SIZE, SIZE)

    ln = len(game.positions)
    for i, p in enumerate(game.positions):
        if i and head == p:
            color = CROSS_COLOR
            game.end = ":("
        else:
            color = SNAKE_COLOR

        ctx.fillStyle = f"rgba({color}, {(ln - i + 2) / ln})"
        ctx.fillRect(p.x * CELL, p.y * CELL, SIZE, SIZE)

    if game.end is not None:
        end_text = "Game over " + game.end
        ctx.fillText(end_text, WIDTH / 2 - ctx.measureText(end_text).width / 2, HEIGHT / 2)


def restart(e):
    global game
    game = Game()


def main():
    document.getElementById("status").innerHTML = 'Loaded and running ...'

    ctx.font = f"{CELL*2}px Arial"
    #document.onkeypress = on_key
    document.addEventListener("keydown", create_proxy(on_key))

    button = document.getElementById("button")
    button.addEventListener("click", create_proxy(restart))

    setInterval(create_proxy(loop), 1_000 / FPS)


main()
