from src.classes.menu import *
from src.classes.laserbuffer import LaserBuffer
from src.classes.vision import VisionCore
from src.classes.gameloader import GameLoader
from src.classes.entity import Entity

class Game:
    def __init__(self):
        pygame.init()

        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.ESC_KEY, self.LEFT_KEY, self.RIGHT_KEY = False, False, False, False, False, False, False

        self.DISPLAY_W, self.DISPLAY_H = 1920, 1080     ##TODO: resolutions change in options
        self.TARGET_W, self.TARGET_H = 1920, 1080

        self.ratio = self.DISPLAY_H / self.TARGET_H

        self.display = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H))
        self.window = pygame.display.set_mode((self.DISPLAY_W, self.DISPLAY_H))

        self.font_name = os.path.abspath("assets/font/8-BIT WONDER.TTF")

        self.BLACK, self.WHITE = (0, 0, 0), (255, 255, 255)
        self.background_color = self.BLACK

        self.main_menu = MainMenu(self)
        self.game_selector = GameSelector(self)
        self.options = Options(self)
        self.screen_calibrations = ScreenCalibration(self)
        self.curr_menu = self.main_menu

        self.laser_buffer = LaserBuffer()
        self.vision_core = VisionCore(self.laser_buffer)
        self.vision_core.start()

        self.game_loader = GameLoader(self)

        self.selected_game = None
        self.is_game_selected = False

        self.all_sprites = None

        self.entities_by_name = {}
        self.active_inputs = {}
        self.input_bindings = {}

    # def game_loop(self):
    #     if self.is_game_selected:
    #         if self.selected_game:
    #             is_level_loaded = self.game_loader.load_game(self.selected_game)
    #
    #             if is_level_loaded:
    #                 self.playing = True
    #
    #             else:
    #                 self.playing = False
    #                 self.is_game_selected = False
    #                 self.curr_menu = self.game_selector
    #
    #                 return
    #
    #     while self.playing:
    #         self.selected_game = None
    #         self.check_events()
    #
    #         if self.ESC_KEY:
    #             self.playing = False
    #
    #         self.display.fill(self.BLACK)
    #
    #         self.draw_text('Press ESC to exit', 20, self.DISPLAY_W / 2, 30, self.WHITE)
    #
    #         pointer_state = self.laser_buffer.get_latest()
    #
    #         if pointer_state:
    #             x = pointer_state.x
    #             y = pointer_state.y
    #             pygame.draw.circle(self.display, (255, 0, 0), (x, y), 20)
    #
    #         self.window.blit(self.display, (0, 0))
    #         pygame.display.update()
    #
    #         self.reset_keys()

    def game_loop(self):
        if self.is_game_selected:
            if self.selected_game:  #selectec game path
                is_level_loaded = self.game_loader.load_game(self.selected_game)

                if is_level_loaded:
                    self.all_sprites = pygame.sprite.Group()
                    self.entities_by_name = {}
                    self.input_bindings = {}

                    layout_data = self.game_loader.get_layout()
                    map_size = layout_data.get('map_size', [20, 20])

                    self.background_color = layout_data.get('background_color', [0, 0, 0])

                    cell_w = self.TARGET_W / map_size[0]
                    cell_h = self.TARGET_H / map_size[1]

                    entities_data = self.game_loader.get_entities()
                    for entity in entities_data:
                        new_entity = Entity(self, entity, cell_w, cell_h)
                        self.all_sprites.add(new_entity)

                        self.entities_by_name[new_entity.name] = new_entity

                    input_data = self.game_loader.get_inputs()
                    for input in input_data:
                        source = input.get('source')
                        target = input.get('target')

                        if target in self.entities_by_name:
                            self.input_bindings[source] = self.entities_by_name[target]

                    self.playing = True

                else:
                    self.playing = False
                    self.is_game_selected = False
                    self.curr_menu.run_display = True
                    return

            else:
                self.playing = False
                self.is_game_selected = False
                self.curr_menu = self.game_selector

                return

        while self.playing:
            self.check_events()

            if self.ESC_KEY:
                self.playing = False
                self.is_game_selected = False
                self.curr_menu = self.game_selector

            self.display.fill(self.background_color)
            self.all_sprites.update()
            self.all_sprites.draw(self.display)

            self.draw_text('Press ESC to exit', 20, self.DISPLAY_W / 2, self.DISPLAY_H/2, (100, 100, 100))

            pointer_state = self.laser_buffer.get_latest()
            if pointer_state:
                x = pointer_state.x
                y = pointer_state.y
                pygame.draw.circle(self.display, (255, 0, 0), (x, y), 20)

                target_entity = self.input_bindings.get("laser_red")
                if target_entity:
                    if "y" in target_entity.constraints:
                        target_entity.rect.centery = y
                    elif "x" in target_entity.constraints:
                        target_entity.rect.centerx = x
                    else:
                        target_entity.rect.center = (x, y)


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
                if event.key == pygame.K_LEFT:
                    self.LEFT_KEY = True
                if event.key == pygame.K_RIGHT:
                    self.RIGHT_KEY = True

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.ESC_KEY, self.LEFT_KEY, self.RIGHT_KEY = False, False, False, False, False, False, False

    def draw_text(self, text, size, x, y, color):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.display.blit(text_surface, text_rect)

    def error_popup(self, text):
        popup_running = True

        self.reset_keys()

        while popup_running:
            self.check_events()

            text_length = len(text) * 40

            box_w = int(text_length * self.ratio)
            box_h = int(300 * self.ratio)
            box_x = (self.DISPLAY_W - box_w) / 2
            box_y = (self.DISPLAY_H - box_h) / 2

            if self.START_KEY:
                popup_running = False
                self.reset_keys()

            pygame.draw.rect(self.display, (30, 30, 30), (box_x, box_y, box_w, box_h))
            pygame.draw.rect(self.display, self.WHITE, (box_x, box_y, box_w, box_h), 4)

            self.draw_text("ERROR", int(40 * self.ratio), self.DISPLAY_W / 2, box_y + (50 * self.ratio), (255, 50, 50))
            self.draw_text(text, int(20 * self.ratio), self.DISPLAY_W / 2, self.DISPLAY_H / 2, self.WHITE)

            ok_y = box_y + box_h - (50 * self.ratio)
            self.draw_text("OK", int(30 * self.ratio), self.DISPLAY_W / 2, ok_y, (0, 255, 0))
            self.draw_text("*", int(35 * self.ratio), (self.DISPLAY_W / 2) - (50 * self.ratio), ok_y, self.WHITE)

            self.window.blit(self.display, (0, 0))
            pygame.display.update()

            self.reset_keys()