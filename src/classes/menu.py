import pygame

class Menu:
    def __init__(self, game):
        self.game = game
        self.mid_w, self.mid_h = self.game.DISPLAY_W/2, self.game.DISPLAY_H/2
        self.run_display = True

        base_font_size = 40
        base_gap = 60
        base_padding = 20
        base_cursor_size = 35


        self.font_size = int(base_font_size * self.game.ratio)
        self.gap = int(base_gap * self.game.ratio)
        self.padding = int(base_padding * self.game.ratio)
        self.cursor_size = int(base_cursor_size * self.game.ratio)

        self.cursor_rect = pygame.Rect(0, 0, self.cursor_size, self.cursor_size)

    def draw_cursor(self):
        self.game.draw_text('*', self.cursor_size, self.cursor_rect.x, self.cursor_rect.y, self.game.WHITE)

    def blit_screen(self):
        self.game.window.blit(self.game.display, (0,0))
        pygame.display.update()
        self.game.reset_keys()

    def calculate_cursor_pos(self, text, y_position):
        font = pygame.font.Font(self.game.font_name, self.font_size)

        text_surface = font.render(text, True, self.game.WHITE)
        text_width = text_surface.get_width()

        x_position = self.mid_w - (text_width / 2) - self.padding

        self.cursor_rect.midtop = (x_position, y_position)

class MainMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = "Play"

        self.play_x, self.play_y = self.mid_w, self.mid_h
        self.screen_calibration_x, self.screen_calibration_y = self.mid_w, self.mid_h + self.gap
        self.options_x, self.options_y = self.mid_w, self.mid_h + (self.gap * 2)
        self.quit_x, self.quit_y = self.mid_w, self.mid_h + (self.gap * 3)

        self.calculate_cursor_pos("Play", self.play_y)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)

            title_size = int(self.font_size * 1.5)
            self.game.draw_text("Main Menu", title_size, self.mid_w, self.mid_h - (self.gap * 4), self.game.WHITE)

            self.game.draw_text("Play", self.font_size, self.play_x, self.play_y, self.game.WHITE)
            self.game.draw_text("Screen Calibration", self.font_size, self.screen_calibration_x, self.screen_calibration_y, self.game.WHITE)
            self.game.draw_text("Options", self.font_size, self.options_x, self.options_y, self.game.WHITE)
            self.game.draw_text("Quit", self.font_size, self.quit_x, self.quit_y, self.game.WHITE)

            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN_KEY:
            if self.state == "Play":
                self.calculate_cursor_pos("Screen Calibration", self.screen_calibration_y)
                self.state = "Screen Calibration"
            elif self.state == "Screen Calibration":
                self.calculate_cursor_pos("Options", self.options_y)
                self.state = "Options"
            elif self.state == "Options":
                self.calculate_cursor_pos("Quit", self.quit_y)
                self.state = "Quit"
            elif self.state == "Quit":
                self.calculate_cursor_pos("Start", self.play_y)
                self.state = "Play"

        elif self.game.UP_KEY:
            if self.state == "Play":
                self.calculate_cursor_pos("Quit", self.quit_y)
                self.state = "Quit"
            elif self.state == "Screen Calibration":
                self.calculate_cursor_pos("Start", self.play_y)
                self.state = "Play"
            elif self.state == "Options":
                self.calculate_cursor_pos("Screen Calibration", self.screen_calibration_y)
                self.state = "Screen Calibration"
            elif self.state == "Quit":
                self.calculate_cursor_pos("Options", self.options_y)
                self.state = "Options"

    def check_input(self):
        self.move_cursor()
        if self.game.START_KEY:
            if self.state == "Play":
                self.game.curr_menu = self.game.game_selector
            elif self.state == "Screen Calibration":
                self.game.curr_menu = self.game.screen_calibrations
            elif self.state == "Options":
                self.game.curr_menu = self.game.options
            elif self.state == "Quit":
                self.game.running = False
            self.run_display = False

class GameSelector(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.start_x, self.start_y = self.mid_w, self.mid_h + (self.gap * 5)


    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)
            self.game.draw_text("Start", self.font_size, self.start_x, self.start_y, self.game.WHITE)
            self.blit_screen()

    def check_input(self):
        if self.game.ESC_KEY:
            self.game.curr_menu = self.game.main_menu
            self.run_display = False

class ScreenCalibration(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)
            self.blit_screen()

    def check_input(self):
        if self.game.ESC_KEY:
            self.game.curr_menu = self.game.main_menu
            self.run_display = False

class Options(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)
            self.blit_screen()

    def check_input(self):
        if self.game.ESC_KEY:
            self.game.curr_menu = self.game.main_menu
            self.run_display = False