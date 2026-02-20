import pygame, os
from src.classes.menu import *
from src.classes.laserbuffer import LaserBuffer
from src.classes.vision import VisionCore

class Game:
    def __init__(self):
        pygame.init()
        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.ESC_KEY = False, False, False, False, False

        self.DISPLAY_W, self.DISPLAY_H = 1920, 1080     ##TODO: resolutions change in options
        self.TARGET_W, self.TARGET_H = 1920, 1080

        self.ratio = self.DISPLAY_H / self.TARGET_H

        self.display = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H))
        self.window = pygame.display.set_mode((self.DISPLAY_W, self.DISPLAY_H))

        self.font_name = os.path.abspath("assets\\font\\8-BIT WONDER.TTF")

        self.BLACK, self.WHITE = (0, 0, 0), (255, 255, 255)

        self.main_menu = MainMenu(self)
        self.game_selector = GameSelector(self)
        self.options = Options(self)
        self.screen_calibrations = ScreenCalibration(self)
        self.curr_menu = self.main_menu

        self.laser_buffer = LaserBuffer()
        self.vision_core = VisionCore(self.laser_buffer)
        self.vision_core.start()


    def game_loop(self):
        while self.playing:
            self.check_events()

            if self.ESC_KEY:
                self.playing = False

            self.display.fill(self.BLACK)

            self.draw_text('Press ESC to exit', 20, self.DISPLAY_W / 2, 30, self.WHITE)

            pointer_state = self.laser_buffer.get_latest()

            if pointer_state:
                x = pointer_state.x
                y = pointer_state.y
                pygame.draw.circle(self.display, (255, 0, 0), (x, y), 20)

            self.window.blit(self.display, (0, 0))
            pygame.display.update()

            self.reset_keys()


    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
                self.curr_menu.run_display = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.START_KEY = True
                if event.key == pygame.K_BACKSPACE:
                    self.BACK_KEY = True
                if event.key == pygame.K_DOWN:
                    self.DOWN_KEY = True
                if event.key == pygame.K_UP:
                    self.UP_KEY = True
                if event.key == pygame.K_ESCAPE:
                    self.ESC_KEY = True

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.ESC_KEY = False, False, False, False, False

    def draw_text(self, text, size, x, y, color):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.display.blit(text_surface, text_rect)