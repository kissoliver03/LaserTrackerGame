import yaml, os

class GameLoader:
    def __init__(self):
        self.is_level_loaded = False
        self.data = None

    def load_game(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath)

        try:
            with open(filepath, "r", encoding= 'utf-8') as file:
                self.data = yaml.safe_load(file)

            self.is_level_loaded = True

            return True

        except FileNotFoundError:
            self.is_level_loaded = False
            return False

        except yaml.YAMLError as exc:
            self.is_level_loaded = False
            return False

        except Exception as exc:
            self.is_level_loaded = False
            return False
