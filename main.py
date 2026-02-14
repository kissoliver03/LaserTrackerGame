from src.game import Game

game = Game()

while game.running:
    game.playing = True
    game.game_loop()