from src.game import Game

game = Game()

while game.running:
    game.curr_menu.display_menu()
    game.game_loop()