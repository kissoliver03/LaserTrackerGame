from src.classes.gameparser import GameParser
from src.classes.entity import Entity
import pygame


class GameLoader:
    def __init__(self, game, game_parser):
        self.game = game
        self.game_parser = game_parser


    def load(self):
        if self.game.is_game_selected:
            if self.game.selected_game:  #selected game path
                is_level_loaded = self.game_parser.parse_game(self.game.selected_game)

                if is_level_loaded:
                    self.game.all_sprites = pygame.sprite.Group()
                    self.game.entities_by_name = {}
                    self.game.input_bindings = {}
                    self.game.sprite_groups = {}

                    layout_data = self.game_parser.get_layout()
                    map_size = layout_data.get('map_size', [32, 18])

                    self.game.background_color = layout_data.get('background_color', [0, 0, 0])

                    self.game.cell_w = self.game.TARGET_W / map_size[0]
                    self.game.cell_h = self.game.TARGET_H / map_size[1]

                    globals_data = self.game_parser.get_globals()
                    self.game.lives = globals_data.get('lives', 3)

                    #Get entities from parsed .YAML
                    entities_data = self.game_parser.get_entities()
                    for entity in entities_data:
                        new_entity = Entity(self, entity, self.game.cell_w, self.game.cell_h)
                        self.game.all_sprites.add(new_entity)

                        self.game.entities_by_name[new_entity.name] = new_entity

                        group_name = new_entity.group
                        if group_name not in self.game.sprite_groups:
                            self.game.sprite_groups[group_name] = pygame.sprite.Group()
                        self.game.sprite_groups[group_name].add(new_entity)


                    #Get inputs from parsed .YAML
                    input_data = self.game.game_parser.get_inputs()
                    for input_item in input_data:
                        name = input_item.get('name')
                        source = input_item.get('source')
                        target = input_item.get('target')

                        if target in self.game.entities_by_name:
                            self.game.input_bindings[source] = self.game.entities_by_name[target]

                        self.game.players[name] = self.game.lives

                    self.game.playing = True

                else:
                    self.game.playing = False
                    self.game.is_game_selected = False
                    self.game.curr_menu.run_display = True
                    return

            else:
                self.game.playing = False
                self.game.is_game_selected = False
                self.game.curr_menu = self.game.game_selector

                return