import os

import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, game, data_dict, cell_w, cell_h):
        super().__init__()
        self.game = game

        self.name = data_dict.get('name', 'unknown')
        self.group = data_dict.get('group', self.name)
        self.type = data_dict.get('type', 'static')
        self.shape = data_dict.get('shape', 'rect')
        self.constraints = data_dict.get('constraints', [])

        grid_pos = data_dict.get('grid_pos', [0, 0])
        size = data_dict.get('size', [1, 1])

        width = int(size[0] * cell_w)
        height = int(size[1] * cell_h)
        x_pos = int(grid_pos[0] * cell_w)
        y_pos = int(grid_pos[1] * cell_h)

        model_path = data_dict.get('model', None)
        is_image_loaded = False

        if model_path:
            abs_model_path = os.path.abspath(model_path)

            try:
                model = pygame.image.load(abs_model_path).convert_alpha()

                self.image = pygame.transform.smoothscale(model, (width, height))
                is_image_loaded = True

            except FileNotFoundError:
                is_image_loaded = False
                self.game.error_popup("Model not found.")

            except pygame.error as exc:
                is_image_loaded = False
                self.game.error_popup("Model error")

        if not is_image_loaded:
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)

            if self.shape == 'rect':
                pygame.draw.rect(self.image, self.game.WHITE, [0,0, width, height])
            elif self.shape == 'circle':
                radius = int(width / 2)
                pygame.draw.circle(self.image, self.game.WHITE, [radius, radius], radius)

        self.rect = self.image.get_rect(topleft=(x_pos, y_pos))

        velocity = data_dict.get('velocity', [0, 0])
        self.vel_x = velocity[0]
        self.vel_y = velocity[1]

    def update(self):
        if self.type in ['dynamic', 'kinematic']:
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y


