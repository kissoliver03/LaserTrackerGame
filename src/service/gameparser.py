import yaml, os

class GameParser:
    def __init__(self, game):
        self.game = game
        self.is_level_loaded = False
        self.data = None

    def parse_game(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath)

        try:
            with open(filepath, "r", encoding= 'utf-8') as file:
                self.data = yaml.safe_load(file)

            if self.data is None:
                self.game.msg_popup("ERROR", [255, 0, 0], "The loaded game is empty")
                self.is_level_loaded = False

                return False

            self.is_level_loaded = True

            return True

        except FileNotFoundError:
            self.is_level_loaded = False
            self.game.msg_popup("ERROR", [255, 0, 0], "Game not found")

            return False

        except yaml.YAMLError as exc:
            self.is_level_loaded = False
            self.game.msg_popup("ERROR", [255, 0, 0], "Error while loading game")

            return False

        except Exception as exc:
            self.is_level_loaded = False
            self.game.msg_popup("ERROR", [255, 0, 0], "Error while loading game")

            return False


    def get_meta(self):
        data = self.data.get('meta', {}) if self.is_level_loaded else {}
        return data if isinstance(data, dict) else {}

    def get_globals(self):
        data = self.data.get('globals', {}) if self.is_level_loaded else {}
        return data if isinstance(data, dict) else {}

    def get_layout(self):
        data = self.data.get('layout', {}) if self.is_level_loaded else {}
        return data if isinstance(data, dict) else {}

    def get_entities(self):
        data = self.data.get('entities', []) if self.is_level_loaded else []
        return data if isinstance(data, list) else []

    def get_inputs(self):
        data = self.data.get('inputs', []) if self.is_level_loaded else []
        return data if isinstance(data, list) else []

    def get_rules(self):
        data = self.data.get('rules', []) if self.is_level_loaded else []
        return data if isinstance(data, list) else []

    def get_templates(self):
        data = self.data.get('templates', []) if self.is_level_loaded else []
        return data if isinstance(data, list) else []