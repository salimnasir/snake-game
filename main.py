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

Window.size = (400, 700)

CELL_SIZE = 20
BEST_SCORE_FILE = "best_score.txt"


# ================= GAME =================
class SnakeGame(Widget):

    def __init__(self, speed=0.15, menu_callback=None, **kwargs):
        super().__init__(**kwargs)

        self.menu_callback = menu_callback

        self.snake = [(5, 5)]
        self.direction = (1, 0)

        self.food = (10, 10)

        # ===== BONUS FOOD =====
        self.bonus_food = None
        self.bonus_visible = False
        self.bonus_timer = 0

        self.score = 0
        self.best_score = self.load_best_score()

        self.score_label = Label(
            text="Score: 0",
            pos=(20, 650),
            font_size=20
        )

        self.best_label = Label(
            text=f"Best: {self.best_score}",
            pos=(250, 650),
            font_size=20
        )

        self.add_widget(self.score_label)
        self.add_widget(self.best_label)

        self.event = Clock.schedule_interval(self.update, speed)

        self.redraw()

    # ================= CONTROLS =================
    def move_up(self, instance):
        if self.direction != (0, -1):
            self.direction = (0, 1)

    def move_down(self, instance):
        if self.direction != (0, 1):
            self.direction = (0, -1)

    def move_left(self, instance):
        if self.direction != (1, 0):
            self.direction = (-1, 0)

    def move_right(self, instance):
        if self.direction != (-1, 0):
            self.direction = (1, 0)

    # ================= DRAW =================
    def redraw(self):

        self.canvas.clear()

        with self.canvas:

            # Background
            Color(0, 0, 0)
            Rectangle(pos=(0, 0), size=(400, 700))

            # Snake
            Color(0, 1, 0)

            for x, y in self.snake:
                Rectangle(
                    pos=(x * CELL_SIZE, y * CELL_SIZE + 120),
                    size=(CELL_SIZE, CELL_SIZE)
                )

            # Normal Food
            Color(1, 0, 0)

            Rectangle(
                pos=(
                    self.food[0] * CELL_SIZE,
                    self.food[1] * CELL_SIZE + 120
                ),
                size=(CELL_SIZE, CELL_SIZE)
            )

            # Bonus Food
            if self.bonus_visible:

                Color(1, 1, 0)

                Rectangle(
                    pos=(
                        self.bonus_food[0] * CELL_SIZE,
                        self.bonus_food[1] * CELL_SIZE + 120
                    ),
                    size=(CELL_SIZE, CELL_SIZE)
                )

    # ================= GAME LOOP =================
    def update(self, dt):

        head_x, head_y = self.snake[0]
        dx, dy = self.direction

        new_head = (head_x + dx, head_y + dy)

        # ===== BORDER PASS THROUGH =====
        if new_head[0] < 0:
            new_head = (19, new_head[1])

        elif new_head[0] > 19:
            new_head = (0, new_head[1])

        if new_head[1] < 0:
            new_head = (new_head[0], 24)

        elif new_head[1] > 24:
            new_head = (new_head[0], 0)

        # ===== SELF COLLISION ONLY =====
        if new_head in self.snake:
            self.game_over()
            return

        self.snake.insert(0, new_head)

        # ===== NORMAL FOOD =====
        if new_head == self.food:

            self.score += 1
            self.score_label.text = f"Score: {self.score}"

            if self.score > self.best_score:
                self.best_score = self.score
                self.best_label.text = f"Best: {self.best_score}"
                self.save_best_score()

            # New food
            self.food = (
                randint(0, 19),
                randint(0, 24)
            )

            # ===== BONUS FOOD APPEAR =====
            if self.score >= 5 and not self.bonus_visible:

                self.bonus_food = (
                    randint(0, 19),
                    randint(0, 24)
                )

                self.bonus_visible = True

                # bonus visible for 5-10 sec
                self.bonus_timer = randint(5, 10)

        # ===== BONUS FOOD =====
        elif self.bonus_visible and new_head == self.bonus_food:

            self.score += 5
            self.score_label.text = f"Score: {self.score}"

            if self.score > self.best_score:
                self.best_score = self.score
                self.best_label.text = f"Best: {self.best_score}"
                self.save_best_score()

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

        self.add_widget(Label(
            text="GAME OVER",
            font_size=40,
            center=(200, 350)
        ))

        btn = Button(
            text="Back To Menu",
            size_hint=(None, None),
            size=(200, 50),
            pos=(100, 300)
        )

        btn.bind(on_press=lambda x: self.menu_callback())

        self.add_widget(btn)


# ================= MENU =================
class MenuScreen(BoxLayout):

    def __init__(self, start_game_callback, **kwargs):

        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.spacing = 20
        self.padding = 50

        self.add_widget(Label(
            text="SNAKE GAME",
            font_size=40
        ))

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

        self.root_layout = BoxLayout(
            orientation="vertical"
        )

        self.show_menu()

        return self.root_layout

    # ================= MENU =================
    def show_menu(self):

        self.root_layout.clear_widgets()

        self.root_layout.add_widget(
            MenuScreen(self.start_game)
        )

    # ================= START GAME =================
    def start_game(self, speed):

        self.root_layout.clear_widgets()

        game = SnakeGame(
            speed=speed,
            menu_callback=self.show_menu
        )

        # ===== CONTROL PAD =====
        controls = BoxLayout(
            size_hint=(1, 0.3),
            orientation="vertical",
            padding=10,
            spacing=5
        )

        row1 = BoxLayout()
        row2 = BoxLayout()
        row3 = BoxLayout()

        up = Button(
            text="⬆",
            font_size=30
        )

        down = Button(
            text="⬇",
            font_size=30
        )

        left = Button(
            text="⬅",
            font_size=30
        )

        right = Button(
            text="➡",
            font_size=30
        )

        up.bind(on_press=game.move_up)
        down.bind(on_press=game.move_down)
        left.bind(on_press=game.move_left)
        right.bind(on_press=game.move_right)

        # Layout
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

        container = BoxLayout(
            orientation="vertical"
        )

        container.add_widget(game)
        container.add_widget(controls)

        self.root_layout.add_widget(container)


# ================= RUN =================
SnakeApp().run()