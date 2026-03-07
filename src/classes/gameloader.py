import yaml, os

class GameLoader:
    def __init__(self, game):
        self.game = game
        self.is_level_loaded = False
        self.data = None

    def load_game(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath)

        try:
            with open(filepath, "r", encoding= 'utf-8') as file:
                self.data = yaml.safe_load(file)

            if self.data is None:
                self.game.error_popup("The loaded game is empty")
                self.is_level_loaded = False

                return False

            self.is_level_loaded = True

            return True

        except FileNotFoundError:
            self.is_level_loaded = False
            self.game.error_popup("Game not found.")

            return False

        except yaml.YAMLError as exc:
            self.is_level_loaded = False
            self.game.error_popup("Error while loading game.")

            return False

        except Exception as exc:
            self.is_level_loaded = False
            self.game.error_popup("Error while loading game.")

            return False


    def get_meta(self):
        if self.is_level_loaded:
            return self.data.get('meta', {})
        else:
            return {}

    def get_globals(self):
        if self.is_level_loaded:
            return self.data.get('globals', {})
        else:
            return {}

    def get_layout(self):
        if self.is_level_loaded:
            return self.data.get('layout', {})
        else:
            return {}

    def get_entities(self):
        if self.is_level_loaded:
            return self.data.get('entities', [])
        else:
            return []

    def get_inputs(self):
        if self.is_level_loaded:
            return self.data.get('inputs', [])
        else:
            return []

    def get_rules(self):
        if self.is_level_loaded:
            return self.data.get('rules', [])
        else:
            return []