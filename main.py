from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from random import randint
import os

Window.clearcolor = (0, 0, 0, 1)

CELL_SIZE = 20
BEST_SCORE_FILE = "best_score.txt"


# ================= GAME =================
class SnakeGame(Widget):

    def __init__(self, speed=0.15, menu_callback=None, hud_callback=None, **kwargs):
        super().__init__(**kwargs)

        self.menu_callback = menu_callback
        self.hud_callback = hud_callback

        self.snake = [(5, 5)]
        self.direction = (1, 0)

        self.food = (10, 10)

        # BONUS FOOD
        self.bonus_food = None
        self.bonus_visible = False
        self.bonus_timer = 0

        self.score = 0
        self.best_score = self.load_best_score()

        self.event = Clock.schedule_interval(self.update, speed)

        self.bind(size=self.redraw, pos=self.redraw)
        self.redraw()

    # ================= CONTROLS =================
    def move_up(self, *args):
        if self.direction != (0, -1):
            self.direction = (0, 1)

    def move_down(self, *args):
        if self.direction != (0, 1):
            self.direction = (0, -1)

    def move_left(self, *args):
        if self.direction != (1, 0):
            self.direction = (-1, 0)

    def move_right(self, *args):
        if self.direction != (-1, 0):
            self.direction = (1, 0)

    # ================= DRAW =================
    def redraw(self, *args):
        self.canvas.clear()

        with self.canvas:
            # background (ONLY GAME AREA)
            Color(0, 0, 0)
            Rectangle(pos=self.pos, size=self.size)

            # snake
            Color(0, 1, 0)
            for x, y in self.snake:
                Rectangle(
                    pos=(x * CELL_SIZE, y * CELL_SIZE),
                    size=(CELL_SIZE, CELL_SIZE)
                )

            # food
            Color(1, 0, 0)
            Rectangle(
                pos=(self.food[0] * CELL_SIZE, self.food[1] * CELL_SIZE),
                size=(CELL_SIZE, CELL_SIZE)
            )

            # bonus
            if self.bonus_visible and self.bonus_food:
                Color(1, 1, 0)
                Rectangle(
                    pos=(self.bonus_food[0] * CELL_SIZE, self.bonus_food[1] * CELL_SIZE),
                    size=(CELL_SIZE, CELL_SIZE)
                )

    # ================= GAME LOOP =================
    def update(self, dt):

        head_x, head_y = self.snake[0]
        dx, dy = self.direction

        new_head = (head_x + dx, head_y + dy)

        max_x = int(self.width // CELL_SIZE)
        max_y = int(self.height // CELL_SIZE)

        new_head = (new_head[0] % max_x, new_head[1] % max_y)

        if new_head in self.snake:
            self.game_over()
            return

        self.snake.insert(0, new_head)

        # ===== NORMAL FOOD =====
        if new_head == self.food:

            self.score += 1
            self.update_hud()

            self.food = (randint(0, max_x - 1), randint(0, max_y - 1))

            # BONUS every 5 points
            if self.score % 5 == 0:
                self.bonus_food = (randint(0, max_x - 1), randint(0, max_y - 1))
                self.bonus_visible = True
                self.bonus_timer = randint(5, 10)

        # ===== BONUS EAT =====
        elif self.bonus_visible and new_head == self.bonus_food:

            self.score += 5
            self.update_hud()

            self.bonus_visible = False
            self.bonus_food = None

        else:
            self.snake.pop()

        # ===== BONUS TIMER =====
        if self.bonus_visible:
            self.bonus_timer -= dt
            if self.bonus_timer <= 0:
                self.bonus_visible = False
                self.bonus_food = None

        self.redraw()

    # ================= HUD =================
    def update_hud(self):
        if self.hud_callback:
            self.hud_callback(self.score, self.best_score)

    # ================= BEST SCORE =================
    def load_best_score(self):
        if os.path.exists(BEST_SCORE_FILE):
            with open(BEST_SCORE_FILE, "r") as f:
                return int(f.read())
        return 0

    def save_best_score(self):
        with open(BEST_SCORE_FILE, "w") as f:
            f.write(str(self.best_score))

    # ================= GAME OVER =================
    def game_over(self):
        self.event.cancel()

        if self.score > self.best_score:
            self.best_score = self.score
            self.save_best_score()

        self.add_widget(Label(
            text="GAME OVER",
            font_size=40,
            center=self.center
        ))

        btn = Button(
            text="Back To Menu",
            size_hint=(None, None),
            size=(200, 60),
            pos=(self.center_x - 100, self.center_y - 100)
        )

        btn.bind(on_press=lambda x: self.menu_callback())
        self.add_widget(btn)


# ================= MENU =================
class MenuScreen(BoxLayout):

    def __init__(self, start_game_callback, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.padding = 40
        self.spacing = 20

        self.add_widget(Label(text="SNAKE GAME", font_size=40))

        easy = Button(text="Easy")
        medium = Button(text="Medium")
        hard = Button(text="Hard")

        easy.bind(on_press=lambda x: start_game_callback(0.20))
        medium.bind(on_press=lambda x: start_game_callback(0.12))
        hard.bind(on_press=lambda x: start_game_callback(0.07))

        self.add_widget(easy)
        self.add_widget(medium)
        self.add_widget(hard)


# ================= APP =================
class SnakeApp(App):

    def build(self):
        self.root_layout = BoxLayout(orientation="vertical")
        self.show_menu()
        return self.root_layout

    def show_menu(self):
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(MenuScreen(self.start_game))

    def start_game(self, speed):

        self.root_layout.clear_widgets()

        main = BoxLayout(orientation="vertical")

        # ================= TOP AREA =================
        top = BoxLayout(size_hint=(1, 0.78), orientation="vertical")

        hud = BoxLayout(size_hint=(1, 0.12))

        self.score_label = Label(text="Score: 0", halign="right")
        self.best_label = Label(text="Best: 0", halign="right")

        hud.add_widget(Label())
        hud.add_widget(self.score_label)
        hud.add_widget(self.best_label)

        game = SnakeGame(
            speed=speed,
            menu_callback=self.show_menu,
            hud_callback=self.update_hud,
            size_hint=(1, 0.88)
        )

        top.add_widget(hud)
        top.add_widget(game)

        # ================= BOTTOM CONTROLS =================
        controls = BoxLayout(size_hint=(1, 0.22), orientation="vertical", padding=10)

        up = Button(text="⬆")
        down = Button(text="⬇")
        left = Button(text="⬅")
        right = Button(text="➡")

        up.bind(on_press=game.move_up)
        down.bind(on_press=game.move_down)
        left.bind(on_press=game.move_left)
        right.bind(on_press=game.move_right)

        row1 = BoxLayout()
        row2 = BoxLayout()
        row3 = BoxLayout()

        row1.add_widget(Label())
        row1.add_widget(up)
        row1.add_widget(Label())

        row2.add_widget(left)
        row2.add_widget(Label())
        row2.add_widget(right)

        row3.add_widget(Label())
        row3.add_widget(down)
        row3.add_widget(Label())

        controls.add_widget(row1)
        controls.add_widget(row2)
        controls.add_widget(row3)

        main.add_widget(top)
        main.add_widget(controls)

        self.root_layout.add_widget(main)

    # HUD UPDATE
    def update_hud(self, score, best):
        self.score_label.text = f"Score: {score}"
        self.best_label.text = f"Best: {best}"


# ================= RUN =================
SnakeApp().run()
