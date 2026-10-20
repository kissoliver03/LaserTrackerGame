import pygame
import os
import time

from src.service.inputloader import InputLoader


class Menu:
    def __init__(self, game):
        self.game = game
        self.mid_w, self.mid_h = self.game.DISPLAY_W/2, self.game.DISPLAY_H/2
        self.run_display = True

        base_font_size = 80
        base_gap = 70
        base_padding = 20
        base_cursor_size = 80


        self.font_size = int(base_font_size * self.game.ratio)
        self.gap = int(base_gap * self.game.ratio)
        self.padding = int(base_padding * self.game.ratio)
        self.cursor_size = int(base_cursor_size * self.game.ratio)

        self.cursor_rect = pygame.Rect(0, 0, self.cursor_size, self.cursor_size)

        self.back_rect = None

        self.hover_start_time = 0
        self.hovered_target = None
        self.hover_duration = 2.0

    def draw_back_button(self):
        large_font_size = int(90 * self.game.ratio)
        large_font = pygame.font.Font(self.game.font_name, large_font_size)
        back_surface = large_font.render("<", True, (255, 255, 0))

        self.back_rect = back_surface.get_rect(topleft=(int(20 * self.game.ratio), int(10 * self.game.ratio)))
        self.game.display.blit(back_surface, self.back_rect)

    def draw_cursor(self):
        self.game.draw_text('*', self.cursor_size, self.cursor_rect.x, self.cursor_rect.y, self.game.WHITE)

    def blit_screen(self):
        self.game.window.blit(self.game.display, (0,0))
        pygame.display.update()
        self.game.reset_keys()

    def calculate_cursor_pos(self, text, y_position, x_offset):
        if x_offset is None:
            x_offset = self.mid_w

        font = pygame.font.Font(self.game.font_name, self.font_size)

        text_surface = font.render(text, True, self.game.WHITE)
        text_width = text_surface.get_width()

        x_position = x_offset - (text_width / 2) - self.padding

        self.cursor_rect.midtop = (x_position, y_position)

    def handle_laser_interaction(self, laser_pos, hitboxes):
        current_target = None
        is_clicked = False

        if not laser_pos:
            self.hovered_target = None
            self.hover_start_time = 0
            return None, False

        laser_x, laser_y = laser_pos

        for name, rect in hitboxes.items():
            if rect and rect.collidepoint(laser_x, laser_y):
                current_target = name
                break

        if current_target:
            if self.hovered_target != current_target:
                self.hovered_target = current_target
                self.hover_start_time = time.time()
            else:
                elapsed = time.time() - self.hover_start_time
                progress = min(1.0, elapsed / self.hover_duration)

                rect = hitboxes[current_target]
                fill_width = int(rect.width * progress)

                if fill_width > 0:
                    bar_height = max(5, int(10 * self.game.ratio))
                    fill_rect = pygame.Rect(rect.x, rect.bottom - bar_height, fill_width, bar_height)
                    pygame.draw.rect(self.game.display, (255, 200, 0), fill_rect)

                pygame.draw.rect(self.game.display, (255, 255, 255), rect, 2)

                if elapsed >= self.hover_duration:
                    is_clicked = True
                    self.hovered_target = None
                    self.hover_start_time = 0
        else:
            self.hovered_target = None
            self.hover_start_time = 0

        return current_target, is_clicked

    def get_laser_pos(self):
        if self.game.mouse_enabled:
            if pygame.mouse.get_pressed()[0]:
                return pygame.mouse.get_pos()
        else:
            if hasattr(self.game, 'vision_core') and self.game.vision_core:
                self.game.vision_core.set_active_sources(["laser_red", "laser_green"])

                for laser_name in ["laser_red", "laser_green"]:
                    buffer = self.game.vision_core.get_buffer(laser_name)
                    if buffer:
                        pointer_state = buffer.get_latest()
                        if pointer_state and pointer_state.laser_visible:
                            return (pointer_state.x, pointer_state.y)
        return None

class MainMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = "Play"

        self.play_x, self.play_y = self.mid_w, self.mid_h
        self.screen_calibration_x, self.screen_calibration_y = self.mid_w, self.mid_h + self.gap
        self.options_x, self.options_y = self.mid_w, self.mid_h + (self.gap * 2)
        self.quit_x, self.quit_y = self.mid_w, self.mid_h + (self.gap * 3)

        self.calculate_cursor_pos("Play", self.play_y, None)

    def display_menu(self):
        self.run_display = True

        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)

            title_size = int(self.font_size * 1.5)
            self.game.draw_text("Main Menu", title_size, self.mid_w, self.mid_h - (self.gap * 4), self.game.WHITE)

            self.game.draw_text("PLAY", self.font_size, self.play_x, self.play_y, self.game.WHITE)
            self.game.draw_text("SCREEN CALIBRATION", self.font_size, self.screen_calibration_x, self.screen_calibration_y, self.game.WHITE)
            self.game.draw_text("OPTIONS", self.font_size, self.options_x, self.options_y, self.game.WHITE)
            self.game.draw_text("QUIT", self.font_size, self.quit_x, self.quit_y, self.game.WHITE)

            font = pygame.font.Font(self.game.font_name, self.font_size)
            hitboxes = {
                "Play": font.render("PLAY", True, self.game.WHITE).get_rect(center=(self.play_x, self.play_y)),
                "Screen Calibration": font.render("SCREEN CALIBRATION", True, self.game.WHITE).get_rect(
                    center=(self.screen_calibration_x, self.screen_calibration_y)),
                "Options": font.render("OPTIONS", True, self.game.WHITE).get_rect(
                    center=(self.options_x, self.options_y)),
                "Quit": font.render("QUIT", True, self.game.WHITE).get_rect(center=(self.quit_x, self.quit_y))
            }

            laser_pos = self.get_laser_pos()
            hovered_button, is_clicked = self.handle_laser_interaction(laser_pos, hitboxes)

            if hovered_button and self.state != hovered_button:
                self.state = hovered_button

                if self.state == "Play":
                    self.calculate_cursor_pos("Play", self.play_y, None)
                elif self.state == "Screen Calibration":
                    self.calculate_cursor_pos("Screen Calibration", self.screen_calibration_y, None)
                elif self.state == "Options":
                    self.calculate_cursor_pos("Options", self.options_y, None)
                elif self.state == "Quit":
                    self.calculate_cursor_pos("Quit", self.quit_y, None)

            if is_clicked:
                self.game.START_KEY = True
                self.check_input()

            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN_KEY:
            if self.state == "Play":
                self.calculate_cursor_pos("Screen Calibration", self.screen_calibration_y, None)
                self.state = "Screen Calibration"
            elif self.state == "Screen Calibration":
                self.calculate_cursor_pos("Options", self.options_y, None)
                self.state = "Options"
            elif self.state == "Options":
                self.calculate_cursor_pos("Quit", self.quit_y, None)
                self.state = "Quit"
            elif self.state == "Quit":
                self.calculate_cursor_pos("Start", self.play_y, None)
                self.state = "Play"

        elif self.game.UP_KEY:
            if self.state == "Play":
                self.calculate_cursor_pos("Quit", self.quit_y, None)
                self.state = "Quit"
            elif self.state == "Screen Calibration":
                self.calculate_cursor_pos("Start", self.play_y, None)
                self.state = "Play"
            elif self.state == "Options":
                self.calculate_cursor_pos("Screen Calibration", self.screen_calibration_y, None)
                self.state = "Screen Calibration"
            elif self.state == "Quit":
                self.calculate_cursor_pos("Options", self.options_y, None)
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

        self.DARK_YELLOW = (150, 150, 0)
        self.LIGHT_YELLOW = (255, 200, 0)
        self.GREY = (100, 100, 100)
        self.BOX_IDLE = (50, 60, 80)
        self.BOX_HOVER = (100, 150, 255)

        self.start_x, self.start_y = self.mid_w, self.mid_h + (self.gap * 5)

        self.games_dir = os.path.abspath('assets/games')
        self.game_files = []

        self.current_index = 0
        self.last_index = 0
        self.selected_game = None
        self.last_selected_game = None
        self.on_start_button = False

        self.box_w = int(320 * self.game.ratio)
        self.box_h = int(220 * self.game.ratio)
        self.box_padding = int(40 * self.game.ratio)

        self.items_per_row = 4


    def load_game_files(self):
        if hasattr(self.game, 'valid_games'):
            self.game_files = self.game.valid_games
        else:
            self.game_files = []

    def display_menu(self):
        self.current_index = 0
        self.last_index = 0
        self.selected_game = None
        self.last_selected_game = None
        self.on_start_button = False

        self.visible_start_row = 0

        self.load_game_files()

        self.run_display = True

        self.game.reset_keys()
        pygame.event.clear()

        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)

            self.game.draw_text("Select Game", int(self.font_size * 1.25), self.mid_w, self.mid_h - self.gap * 6,
                                self.game.WHITE)

            number_of_games = len(self.game_files)

            if number_of_games == 0:
                self.game.draw_text("No games were found", self.font_size, self.mid_w, self.mid_h, self.game.WHITE)
            else:
                max_visible_rows = 2
                current_row = self.current_index // self.items_per_row
                total_rows = (number_of_games + self.items_per_row - 1) // self.items_per_row

                if current_row < self.visible_start_row:
                    self.visible_start_row = current_row
                elif current_row >= self.visible_start_row + max_visible_rows:
                    self.visible_start_row = current_row - max_visible_rows + 1

                cols = min(number_of_games, self.items_per_row)
                total_width = (cols * self.box_w) + (cols - 1) * self.box_padding

                box_start_x = self.mid_w - (total_width / 2)

                box_start_y = self.mid_h - self.gap - (self.box_h / 1.2)

                for i, file_name in enumerate(self.game_files):
                    row = i // self.items_per_row
                    col = i % self.items_per_row

                    if row < self.visible_start_row or row >= self.visible_start_row + max_visible_rows:
                        continue

                    relative_row = row - self.visible_start_row

                    x_pos = box_start_x + (col * (self.box_w + self.box_padding))
                    y_pos = box_start_y + (relative_row * (self.box_h + self.box_padding))

                    rect = pygame.Rect(x_pos, y_pos, self.box_w, self.box_h)

                    if file_name == self.selected_game:
                        color = self.DARK_YELLOW
                    elif i == self.current_index and not self.on_start_button:
                        color = self.BOX_HOVER
                    else:
                        color = self.BOX_IDLE

                    pygame.draw.rect(self.game.display, color, rect)
                    pygame.draw.rect(self.game.display, self.game.WHITE, rect, 3)

                    display_name = file_name.replace(".yaml", "")
                    if len(display_name) > 12:
                        display_name = display_name[:10] + ".."

                    self.game.draw_text(display_name, int(self.font_size * 0.7), x_pos + self.box_w / 2,
                                        y_pos + self.box_h / 2, self.game.WHITE)

                if total_rows > max_visible_rows:
                    scrollbar_x = box_start_x + total_width + int(40 * self.game.ratio)
                    scrollbar_y = box_start_y
                    scrollbar_h = (max_visible_rows * self.box_h) + ((max_visible_rows - 1) * self.box_padding)

                    self.game.draw_text("^", int(self.font_size * 0.8), scrollbar_x + 10,
                                        scrollbar_y - int(30 * self.game.ratio), self.game.WHITE)
                    self.game.draw_text("v", int(self.font_size * 0.8), scrollbar_x + 10,
                                        scrollbar_y + scrollbar_h + int(30 * self.game.ratio), self.game.WHITE)

                    pygame.draw.line(self.game.display, self.GREY, (scrollbar_x + 10, scrollbar_y),
                                     (scrollbar_x + 10, scrollbar_y + scrollbar_h), 4)

                    thumb_h = max(int(40 * self.game.ratio), scrollbar_h * (max_visible_rows / total_rows))
                    progress = self.visible_start_row / (total_rows - max_visible_rows)
                    thumb_y = scrollbar_y + progress * (scrollbar_h - thumb_h)

                    thumb_rect = pygame.Rect(scrollbar_x, thumb_y, 20, int(thumb_h))
                    pygame.draw.rect(self.game.display, self.game.WHITE, thumb_rect)

            if self.on_start_button:
                start_button_color = self.LIGHT_YELLOW
                self.calculate_cursor_pos("Start", self.start_y, None)
                self.draw_cursor()
            else:
                start_button_color = self.GREY

            self.game.draw_text("Start", self.font_size, self.start_x, self.start_y, start_button_color)

            self.draw_back_button()

            hitboxes = {}

            if self.back_rect:
                hitboxes["Back"] = self.back_rect

            start_font = pygame.font.Font(self.game.font_name, self.font_size)
            hitboxes["Start"] = start_font.render("Start", True, self.game.WHITE).get_rect(
                center=(self.start_x, self.start_y))

            if number_of_games > 0:
                for i, file_name in enumerate(self.game_files):
                    row = i // self.items_per_row
                    col = i % self.items_per_row
                    if row < self.visible_start_row or row >= self.visible_start_row + max_visible_rows:
                        continue
                    relative_row = row - self.visible_start_row
                    x_pos = box_start_x + (col * (self.box_w + self.box_padding))
                    y_pos = box_start_y + (relative_row * (self.box_h + self.box_padding))

                    hitboxes[file_name] = pygame.Rect(x_pos, y_pos, self.box_w, self.box_h)

            laser_pos = self.get_laser_pos()
            if laser_pos:
                hovered_button, is_clicked = self.handle_laser_interaction(laser_pos, hitboxes)

                if hovered_button:
                    if hovered_button == "Back":
                        pass
                    elif hovered_button == "Start":
                        self.on_start_button = True
                    else:
                        self.on_start_button = False
                        self.selected_game = hovered_button
                        self.current_index = self.game_files.index(hovered_button)

                if is_clicked:
                    if hovered_button == "Back":
                        self.on_start_button = False
                        self.game.ESC_KEY = True
                    else:
                        self.game.START_KEY = True
                    self.check_input()

            self.blit_screen()

    def check_input(self):
        if self.game.ESC_KEY:
            if not self.on_start_button:
                self.game.curr_menu = self.game.main_menu
                self.run_display = False
            else:
                self.current_index = self.last_index
                self.selected_game = None
                self.on_start_button = False

        elif self.game.LEFT_KEY:
            if not self.on_start_button and len(self.game_files) > 0:
                self.current_index = (self.current_index - 1) % len(self.game_files)

        elif self.game.RIGHT_KEY:
            if not self.on_start_button and len(self.game_files) > 0:
                self.current_index = (self.current_index + 1) % len(self.game_files)

        elif self.game.UP_KEY:
            if not self.on_start_button and len(self.game_files) > 0:
                if self.current_index >= self.items_per_row:
                    self.current_index -= self.items_per_row

        elif self.game.DOWN_KEY:
            if not self.on_start_button and len(self.game_files) > 0:
                if self.current_index + self.items_per_row < len(self.game_files):
                    self.current_index += self.items_per_row
                else:
                    self.current_index = len(self.game_files) - 1

        elif self.game.START_KEY:
            if len(self.game_files) > 0:
                if not self.on_start_button:
                    self.selected_game = self.game_files[self.current_index]
                    self.last_selected_game = self.selected_game
                    self.last_index = self.current_index
                    self.on_start_button = True
                else:
                    self.game.selected_game = os.path.join(self.games_dir, self.selected_game)
                    self.game.is_game_selected = True
                    self.run_display = False

class ScreenCalibration(Menu):
    def __init__(self, game, vision_core):
        Menu.__init__(self, game)
        self.vision_core = vision_core
        self.mouse_was_pressed = False

        self.instructions = [
            "Press TOP LEFT of the screen",
            "Press TOP RIGHT of the screen",
            "Press BOTTOM LEFT of the screen",
            "Press BOTTOM RIGHT of the screen",
            "Screen calibration was successful! Press ESC to exit",
        ]

        self.camera_corners = []

    def display_menu(self):
        self.run_display = True
        self.mouse_was_pressed = False

        if self.game.vision_core:
            self.vision_core.reset_calibration()

        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)


            frame = None
            if self.game.vision_core:
                with self.game.vision_core.frame_lock:
                    if self.game.vision_core.latest_frame is not None:
                        frame = self.game.vision_core.latest_frame.copy()

            if frame is not None:
                frame_surface = pygame.image.frombuffer(frame.flatten(), frame.shape[1::-1], 'RGB')

                cam_x = int((self.game.TARGET_W - frame.shape[1]) / 2)
                cam_y = int((self.game.TARGET_H - frame.shape[0]) / 2)
                self.game.display.blit(frame_surface, (cam_x, cam_y))



                step = len(self.vision_core.calibration_points)

                def draw_crosshair(x, y):
                    pygame.draw.circle(self.game.display, self.game.BLACK, (x, y), 55, 20)
                    pygame.draw.line(self.game.display, self.game.BLACK, (x - 85, y), (x + 85, y), 20)
                    pygame.draw.line(self.game.display, self.game.BLACK, (x, y - 85), (x, y + 85), 20)

                    pygame.draw.circle(self.game.display, (255, 50, 50), (x, y), 55, 10)
                    pygame.draw.line(self.game.display, (255, 50, 50), (x - 82, y), (x + 82, y), 10)
                    pygame.draw.line(self.game.display, (255, 50, 50), (x, y - 82), (x, y + 82), 10)

                    pygame.draw.circle(self.game.display, (255, 50, 50), (x, y), 12)

                if step == 0:
                    draw_crosshair(0, 0)
                elif step == 1:
                    draw_crosshair(self.game.TARGET_W, 0)
                elif step == 2:
                    draw_crosshair(0, self.game.TARGET_H)
                elif step == 3:
                    draw_crosshair(self.game.TARGET_W, self.game.TARGET_H)

                mouse_is_pressed = pygame.mouse.get_pressed()[0]

                if mouse_is_pressed and not self.mouse_was_pressed:
                    mx, my = pygame.mouse.get_pos()

                    if cam_x <= mx <= cam_x + frame.shape[1] and cam_y <= my <= cam_y + frame.shape[0]:
                        rel_x = mx - cam_x
                        rel_y = my - cam_y

                        self.game.vision_core.add_calibration_point(rel_x, rel_y)

                self.mouse_was_pressed = mouse_is_pressed

                for pt in self.game.vision_core.calibration_points:
                    px = cam_x + pt[0]
                    py = cam_y + pt[1]
                    pygame.draw.circle(self.game.display, self.game.BLACK, (int(px), int(py)), 8)
                    pygame.draw.circle(self.game.display, (0, 255, 255), (int(px), int(py)), 6)

            step = min(len(self.game.vision_core.calibration_points), 4)
            instruction_text = self.instructions[step]

            font = pygame.font.Font(self.game.font_name, int(self.font_size * 0.75))
            text_surface = font.render(instruction_text, True, self.game.WHITE)
            text_rect = text_surface.get_rect(center=(self.mid_w, self.mid_h))

            bg_rect = text_rect.inflate(40, 20)
            pygame.draw.rect(self.game.display, (30, 30, 30), bg_rect)
            pygame.draw.rect(self.game.display, (255, 200, 0), bg_rect, 2)

            self.game.display.blit(text_surface, text_rect)

            self.blit_screen()

    def check_input(self):
        if self.game.ESC_KEY:
            if hasattr(self, 'vision_core') and self.vision_core is not None:
                self.vision_core.finalize_calibration(self.game.DISPLAY_W, self.game.DISPLAY_H)

            self.game.curr_menu = self.game.main_menu
            self.run_display = False

class Options(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.input_loader = InputLoader()

        self.camera_x, self.camera_y = self.mid_w, self.mid_h
        self.mouse_x, self.mouse_y = self.mid_w, self.mid_h + self.gap
        self.music_x, self.music_y = self.mid_w, self.mid_h + 2 * self.gap

    def display_menu(self):
        self.state = "Camera"
        self.calculate_cursor_pos("Camera input: ", self.camera_y, self.camera_x - self.gap * 6)

        self.run_display = True

        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.fill(self.game.BLACK)

            current_cam_name = self.input_loader.get_camera_name(self.game.selected_camera_id)

            self.game.draw_text("Mouse control: ", self.font_size, self.mouse_x - self.gap * 6, self.mouse_y, self.game.WHITE)
            self.game.draw_text("< %r >" % self.game.mouse_enabled, self.font_size, self.mouse_x + self.gap * 6, self.mouse_y, self.game.WHITE)

            self.game.draw_text("Camera input: ", self.font_size, self.camera_x - self.gap * 6, self.camera_y, self.game.WHITE)
            self.game.draw_text(f"< {current_cam_name} >", self.font_size, self.camera_x + self.gap * 6, self.camera_y, self.game.WHITE)

            self.game.draw_text("Music: ", self.font_size, self.music_x - self.gap * 6, self.music_y, self.game.WHITE)
            self.game.draw_text(f"< {self.game.music_enabled} >", self.font_size, self.music_x + self.gap * 6, self.music_y, self.game.WHITE)

            self.draw_cursor()
            self.draw_back_button()

            hitboxes = {}
            if self.back_rect:
                hitboxes["Back"] = self.back_rect

            font = pygame.font.Font(self.game.font_name, self.font_size)

            def add_arrow_hitboxes(name, text, center_x, center_y):
                text_width = font.size(text)[0]
                box_size = int(self.font_size * 0.8)

                left_rect = pygame.Rect(0, 0, box_size, box_size)
                left_rect.center = (center_x - text_width / 2 + box_size / 2, center_y)

                right_rect = pygame.Rect(0, 0, box_size, box_size)
                right_rect.center = (center_x + text_width / 2 - box_size / 2, center_y)

                hitboxes[f"{name}_Left"] = left_rect
                hitboxes[f"{name}_Right"] = right_rect

            val_x = self.camera_x + self.gap * 6
            add_arrow_hitboxes("Camera", f"< {current_cam_name} >", val_x, self.camera_y)
            add_arrow_hitboxes("Mouse", f"< {self.game.mouse_enabled} >", val_x, self.mouse_y)
            add_arrow_hitboxes("Music", f"< {self.game.music_enabled} >", val_x, self.music_y)

            laser_pos = self.get_laser_pos()
            hovered_button, is_clicked = self.handle_laser_interaction(laser_pos, hitboxes)

            if hovered_button and hovered_button != "Back":
                base_state = hovered_button.split("_")[0]
                if self.state != base_state:
                    self.state = base_state
                    if self.state == "Camera":
                        self.calculate_cursor_pos("Camera input: ", self.camera_y, self.camera_x - self.gap * 6)
                    elif self.state == "Mouse":
                        self.calculate_cursor_pos("Mouse control: ", self.mouse_y, self.mouse_x - self.gap * 6)
                    elif self.state == "Music":
                        self.calculate_cursor_pos("Music: ", self.music_y, self.music_x - self.gap * 6)

            if is_clicked:
                if hovered_button == "Back":
                    self.game.ESC_KEY = True
                elif hovered_button.endswith("_Left"):
                    self.game.LEFT_KEY = True
                elif hovered_button.endswith("_Right"):
                    self.game.RIGHT_KEY = True
                self.check_input()

            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN_KEY:
            if self.state == "Camera":
                self.calculate_cursor_pos("Mouse control: ", self.mouse_y, self.mouse_x - self.gap * 6)
                self.state = "Mouse"

            elif self.state == "Mouse":
                self.calculate_cursor_pos("Music: ", self.music_y, self.music_x - self.gap * 6)
                self.state = "Music"

            elif self.state == "Music":
                self.calculate_cursor_pos("Camera input: ", self.camera_y, self.camera_x - self.gap * 6)
                self.state = "Camera"

        elif self.game.UP_KEY:
            if self.state == "Mouse":
                self.calculate_cursor_pos("Camera input: ", self.camera_y, self.camera_x - self.gap * 6)
                self.state = "Camera"

            elif self.state == "Camera":
                self.calculate_cursor_pos("Music: ", self.music_y, self.music_x - self.gap * 6)
                self.state = "Music"

            elif self.state == "Music":
                self.calculate_cursor_pos("Mouse control: ", self.mouse_y, self.mouse_x - self.gap * 6)
                self.state = "Mouse"


    def check_input(self):
        self.move_cursor()
        cam_count = self.input_loader.get_camera_count()

        if self.game.ESC_KEY:
            if hasattr(self.game, 'vision_core') and self.game.vision_core is not None:
                current_running_id = getattr(self.game.vision_core, 'camera_id', None)

                if current_running_id != self.game.selected_camera_id:
                    self.game.vision_core.stop()
                    self.game.vision_core.start(self.game.selected_camera_id)

            self.game.curr_menu = self.game.main_menu
            self.run_display = False

        elif self.game.RIGHT_KEY:
            if self.state == "Camera":
                if cam_count > 0:
                    self.game.selected_camera_id = (self.game.selected_camera_id + 1) % cam_count

            elif self.state == "Mouse":
                if self.game.mouse_enabled:
                    self.game.mouse_enabled = False
                else:
                    self.game.mouse_enabled = True

            elif self.state == "Music":
                if self.game.music_enabled:
                    self.game.music_enabled = False
                    self.game.main_menu_music.stop()
                else:
                    self.game.music_enabled = True
                    self.game.main_menu_music.play()

        elif self.game.LEFT_KEY:
            if self.state == "Camera":
                if cam_count > 0:
                    self.game.selected_camera_id = (self.game.selected_camera_id - 1) % cam_count

            elif self.state == "Mouse":
                if self.game.mouse_enabled:
                    self.game.mouse_enabled = False
                else:
                    self.game.mouse_enabled = True

            elif self.state == "Music":
                if self.game.music_enabled:
                    self.game.music_enabled = False
                    self.game.main_menu_music.stop()
                else:
                    self.game.music_enabled = True
                    self.game.main_menu_music.play()
