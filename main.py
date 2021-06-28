from kivy.config import Config
Config.set('graphics', 'width', '1030')
Config.set('graphics', 'height', '400')

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy import platform
from kivy.lang.builder import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle


from random import randint
import os
import json


Builder.load_file("menu.kv")


class MainWidget(RelativeLayout):
    from transforms import transform, transform_2D, transform_perpective
    from controls import _keyboard_closed, _on_keyboard_down, _on_keyboard_up, on_touch_down, on_touch_up

    menu_widget = ObjectProperty()
    menu_title = StringProperty("G  A  L  A  X  Y")
    menu_button_title = StringProperty("START")
    score = NumericProperty(0)
    high_score = NumericProperty(0)
    perspective_x = NumericProperty(0)
    perspective_y = NumericProperty(0)

    STATE_FILE = 'state.json'

    vertical_lines = []
    NO_V_LINES = 8
    V_SPACING = .3

    horizontal_lines = []
    NO_H_LINES = 15
    H_SPACING = .1

    SPEED = 0.6
    SPEED_X = 2.0
    current_offset_y = 0
    current_offset_x = 0
    current_speed_x = 0
    current_y_loop = 0

    NO_TILES = 16
    tiles = []
    tiles_coordinates = []


    ship = None
    SHIP_WIDTH = 0.16
    SHIP_HEIGHT = 0.085
    SHIP_BASE_Y = 0.03
    ship_coordinates = [(0,0), (0,0), (0,0), (0,0)]

    game_over = False
    game_has_started = False


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        self.get_state()
        self.init_audio()

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)

        Clock.schedule_interval(self.update, 1/60)

    def reset_game(self):

        self.current_offset_y = 0
        self.current_offset_x = 0
        self.current_speed_x = 0
        self.current_y_loop = 0
        self.tiles_coordinates = []
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        self.score = self.current_y_loop

        self.game_over = False

    def get_state(self):
        if os.path.exists(self.STATE_FILE):
            with open(self.STATE_FILE, 'r') as file:
                data = json.loads(file.read())
                self.high_score = data["high_score"]
                file.close()

    def set_state(self):
        r = open(self.STATE_FILE)
        data = json.load(r)
        with open(self.STATE_FILE, 'w') as file:
            data['high_score'] = self.high_score
            json.dump(data, file)
            file.close()


    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_music.volume = 1
        self.sound_begin.volume = .25
        self.sound_galaxy.volume = .25
        self.sound_gameover_voice.volume = .25
        self.sound_restart.volume = .25
        self.sound_gameover_impact.volume = .6

        self.sound_music.loop = True

        self.sound_galaxy.play()

    def is_desktop(self):
        print(platform)
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.NO_V_LINES):
                self.vertical_lines.append(Line())

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.NO_H_LINES):
                self.horizontal_lines.append(Line())

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.NO_TILES):
                self.tiles.append(Quad())

    def init_ship(self):
        with self.canvas:
            self.ship = Quad()

    def pre_fill_tiles_coordinates(self):
        for i in range(10):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self):
        last_y = 0
        last_x = 0
        for i in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_x = last_coordinates[0]
            last_y = last_coordinates[1] + 1

        for i in range(len(self.tiles_coordinates), self.NO_TILES):
            r = randint(0, 2)

            start_index = -int(self.NO_V_LINES/2) + 1
            end_index = start_index + self.NO_V_LINES -2
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2

            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            last_y += 1

    def get_line_x_from_index(self, index):
        central_x = self.perspective_x - self.current_offset_x
        space = self.V_SPACING * self.width
        offset = index - 0.5
        line_x = int(central_x + offset * space)
        return line_x

    def get_line_y_from_index(self, index):
        space = self.H_SPACING * self.height
        line_y = index * space -self.current_offset_y
        return line_y


    def update_vertical_lines(self):
        start_index = -int(self.NO_V_LINES/2) + 1
        end_index = start_index + self.NO_V_LINES

        for i in range(start_index, end_index):
            line_x = self.get_line_x_from_index(i)
            #print(f"x1 : {line_x} y1: 0  x2 : {line_x} y2: {self.perspective_y}")
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def update_horizontal_lines(self):
        start_index = -int(self.NO_V_LINES/2) + 1
        end_index = start_index + self.NO_V_LINES -1
        min_x = self.get_line_x_from_index(start_index)
        max_x = self.get_line_x_from_index(end_index)

        for i in range(self.NO_H_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(min_x, line_y)
            x2, y2 = self.transform(max_x, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y -= self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_tiles(self):
        for i in range(self.NO_TILES):
            tiles_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tiles_coordinates[0], tiles_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tiles_coordinates[0]+1, tiles_coordinates[1]+1)

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            self.tiles[i].points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_ship(self):
        central_x = self.perspective_x
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height
        self.ship_coordinates[0] = (central_x + ship_half_width, base_y)
        self.ship_coordinates[1] = (central_x - ship_half_width, base_y)
        self.ship_coordinates[2] = (central_x - ship_half_width, base_y + ship_height)
        self.ship_coordinates[3] = (central_x + ship_half_width, base_y + ship_height)
        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        x4, y4 = self.transform(*self.ship_coordinates[3])
        self.ship.points = [x1, y1, x2, y2, x3, y3, x4, y4]
        self.ship.source= 'images/ship3.png'


    def check_ship_collision_with_tiles(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x+1, ti_y+1)

        for i in range(3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <=ymax:
                return True
        return False

    def check_ship_collision(self):
        for i in range(len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tiles(ti_x, ti_y):
                return True
        return False


    def update(self, dt):
        time_factor = dt*60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        if not self.game_over and self.game_has_started:
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y * time_factor
            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor

            spacing_y = self.H_SPACING * self.height

            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score = self.current_y_loop
                if self.score >= self.high_score:
                    self.high_score = self.score
                if self.score % 50 == 0:
                    self.SPEED += .1
                    print(self.SPEED)
                self.generate_tiles_coordinates()

        if not self.check_ship_collision() and not self.game_over:
            self.game_over = True
            self.menu_widget.opacity = 1
            self.sound_gameover_impact.play()
            self.set_state()
            self.menu_title = "G  A  M  E   O  V  E  R"
            self.menu_button_title = "RESTART"
            self.sound_music.stop()
            Clock.schedule_once(self.game_over_voice, 1.5)
            print("Game Over")

    def game_over_voice(self, dt):
        if self.game_over:
            self.sound_gameover_voice.play()


    def on_menu_button(self):
        if self.game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music.play()
        self.game_has_started = True
        print("game is start..")
        self.reset_game()
        self.menu_widget.opacity = 0





class GalaxyApp(MDApp):
    pass


if __name__ == "__main__":
    app = GalaxyApp()
    app.run()
