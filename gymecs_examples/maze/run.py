from gymecs.game import AutoResetGame
from gymecs_examples.maze.game import SingleMazeGame

game=SingleMazeGame(size=(21,21))
game=AutoResetGame(game)
worldapi=game.reset(seed=0)


while not game.is_done():
    game.step()