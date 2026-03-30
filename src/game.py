import operator
import random

import pygame.sprite

from src.classes.menu import *
from src.classes.laserbuffer import LaserBuffer
from src.classes.vision import VisionCore
from src.classes.gameloader import GameLoader
from src.classes.gameparser import GameParser

class Game:
    def __init__(self):
        pygame.init()

        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY, self.ESC_KEY, self.LEFT_KEY, self.RIGHT_KEY = False, False, False, False, False, False, False

        self.DISPLAY_W, self.DISPLAY_H = 1920, 1080     ##TODO: resolutions change in options
        self.TARGET_W, self.TARGET_H = 1920, 1080

        self.ratio = self.DISPLAY_H / self.TARGET_H

        self.display = pygame.Surface((self.TARGET_W, self.TARGET_H))
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
        self.pointer_state = None
        self.vision_core = VisionCore(self.laser_buffer)
        self.vision_core.start()

        self.game_parser = GameParser(self)

        self.game_loader = GameLoader(self, self.game_parser)

        self.selected_game = None
        self.is_game_selected = False

        self.all_sprites = None

        self.cell_h = None
        self.cell_w = None
        self.map_size = None

        self.entities_by_name = {}
        self.active_inputs = {}
        self.input_bindings = {}

        self.operators = {
            "<": operator.lt,
            ">": operator.gt,
            "<=": operator.le,
            ">=": operator.ge,
            "==": operator.eq,
            "!=": operator.ne
        }

        self.sprite_groups = {}

        self.players = {}
        self.score = None


    def game_loop(self):
        self.game_loader.load()

        target_entity = self.input_bindings.get("laser_red")
        if target_entity:
            self.vision_core.last_x = target_entity.rect.centerx
            self.vision_core.last_y = target_entity.rect.centery

        self.pointer_state = self.laser_buffer.clear()

        while self.playing:
            self.check_events()

            if self.ESC_KEY:
                self.playing = False
                self.is_game_selected = False
                self.curr_menu = self.game_selector

            for player_name, stats in self.players.items():
                if stats["lives"] <= 0:
                    self.msg_popup("GAME OVER", f"{player_name} lost")
                    self.playing = False
                    self.is_game_selected = False
                    self.curr_menu = self.game_selector
                    break

                elif stats["score"] >= self.score:
                    self.msg_popup("YOU WIN", f"{player_name} won")
                    self.playing = False
                    self.is_game_selected = False
                    self.curr_menu = self.game_selector
                    break


            self.display.fill(self.background_color)

            self.all_sprites.update()
            self.rule_processor()
            self.all_sprites.draw(self.display)

            self.draw_text('Press ESC to exit', 20, self.DISPLAY_W / 2, self.DISPLAY_H/2, (100, 100, 100))

            self.pointer_state = self.laser_buffer.get_latest()
            if self.pointer_state:
                x = self.pointer_state.x
                y = self.pointer_state.y
                # pygame.draw.circle(self.display, (255, 0, 0), (x, y), 20)

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

    def msg_popup(self, title, text):
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

            self.draw_text(title, int(40 * self.ratio), self.DISPLAY_W / 2, box_y + (50 * self.ratio), (255, 50, 50))
            self.draw_text(text, int(20 * self.ratio), self.DISPLAY_W / 2, self.DISPLAY_H / 2, self.WHITE)

            ok_y = box_y + box_h - (50 * self.ratio)
            self.draw_text("OK", int(30 * self.ratio), self.DISPLAY_W / 2, ok_y, (0, 255, 0))
            self.draw_text("*", int(35 * self.ratio), (self.DISPLAY_W / 2) - (50 * self.ratio), ok_y, self.WHITE)

            self.window.blit(self.display, (0, 0))
            pygame.display.update()

            self.reset_keys()


    def rule_processor(self):
        rules_data = self.game_parser.get_rules()

        for rule in rules_data:
            condition = rule.get("condition", {})
            actions = rule.get("action", [])

            condition_type = condition.get("type", {})
            condition_target = condition.get("targets", [])

            rule_triggered = False
            triggered_entities = []

            if condition_type == "collision":
                group_1 = self.sprite_groups.get(condition_target[0])
                group_2 = self.sprite_groups.get(condition_target[1])

                if group_1 and group_2:
                    collisions = pygame.sprite.groupcollide(group_1, group_2, False, False)

                    if collisions:
                        rule_triggered = True
                        triggered_entities.extend(collisions.keys())

            elif condition_type == "position" and len(condition_target) == 1:
                target_group = self.sprite_groups.get(condition_target[0])

                if target_group:
                    condition_axis = condition.get("axis", {})
                    condition_operator = condition.get("operator", {})
                    condition_value = condition.get("value", 0)

                    operator_function = self.operators.get(condition_operator)

                    if operator_function and condition_axis in ["x", "y"]:

                        for sprite in target_group:

                            if condition_axis == "x":
                                limit = self.cell_w * condition_value
                                current_pos = sprite.rect.centerx
                            else:
                                limit = self.cell_h * condition_value
                                current_pos = sprite.rect.centery

                            if operator_function(current_pos, limit):
                                rule_triggered = True
                                triggered_entities.append(sprite)



            if rule_triggered:
                for action in actions:
                    action_type = action.get("type", {})

                    if action_type == "bounce":
                        axis = action.get("axis", {})

                        for entity in triggered_entities:
                            if axis == "x":
                                entity.vel_x *= -1

                            elif axis == "y":
                                entity.vel_y *= -1

                    elif action_type == "respawn":
                        action_targets = action.get("targets", [])
                        action_position = action.get("pos", None)
                        action_random_position = action.get("random_position", False)

                        entities_to_respawn = []

                        if action_targets:
                            for target in action_targets:
                                entity = self.entities_by_name.get(target)
                                if entity:
                                    entities_to_respawn.append(entity)

                        else:
                            entities_to_respawn = triggered_entities


                        for entity in entities_to_respawn:
                            if action_position is not None:
                                pos_w = self.cell_w * action_position[0]
                                pos_h = self.cell_h * action_position[1]

                            elif action_random_position:
                                safe_grid = self.get_safe_random_positions()

                                pos_w = self.cell_w * safe_grid[0]
                                pos_h = self.cell_h * safe_grid[1]

                            else:
                                pos_w = 0
                                pos_h = 0

                            entity.rect.x = pos_w
                            entity.rect.y = pos_h
                            entity.vel_x = random.randint(1, 3)
                            entity.vel_y = random.randint(1, 3)

                            if not entity.alive():
                                self.all_sprites.add(entity)

                                group_name = entity.group
                                if group_name in self.sprite_groups:
                                    self.sprite_groups[group_name].add(entity)


                    elif action_type == "damage":
                        action_targets = action.get("targets", [])
                        action_value = action.get("value", 1)

                        if action_targets:
                            for target in action_targets:
                                if target in self.players:
                                    self.players[target]["lives"] -= action_value

                    elif action_type == "destroy":
                        action_targets = action.get("targets", [])

                        if action_targets:
                            for target in action_targets:
                                entity = self.entities_by_name.get(target)
                                if entity:
                                    pygame.sprite.Sprite.kill(entity)

                    elif action_type == "add_score":
                        action_targets = action.get("targets", [])
                        action_value = action.get("value", 1)

                        if action_targets:
                            for target in self.players:
                                self.players[target]["score"] += action_value




    def get_safe_random_positions(self):  ##TODO: fix overlapping if object size > [1, 1]
        max_grid_w = self.map_size[0]
        max_grid_h = self.map_size[1]

        free_grids = set()
        for x in range(max_grid_w):
            for y in range(max_grid_h):
                free_grids.add((x, y))

        for entity in self.all_sprites:
            start_x = int(entity.rect.left // self.cell_w)
            end_x = int((entity.rect.right - 1) // self.cell_w)
            start_y = int(entity.rect.top // self.cell_h)
            end_y = int((entity.rect.bottom - 1) // self.cell_h)

            if entity.type == "kinematic":
                if "x" in entity.constraints:
                    for x in range(max_grid_w):
                        for y in range(start_y, end_y + 1):
                            free_grids.discard((x, y))

                elif "y" in entity.constraints:
                    for y in range(max_grid_h):
                        for x in range(start_x, end_x + 1):
                            free_grids.discard((x, y))

            else:
                for x in range(start_x, end_x + 1):
                    for y in range(start_y, end_y + 1):
                        free_grids.discard((x, y))

        if free_grids:
            return random.choice(list(free_grids))
        else:
            return int(max_grid_w / 2), int(max_grid_h / 2)
