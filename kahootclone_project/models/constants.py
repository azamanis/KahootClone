
# Author: Pablo Cuesta Sierra
# contants used in models.model.Game to determine the game state

''' Default state when a game is created, the system
    waits for the participants to join the game. '''
WAITING = 1

''' State to show the next question to the players with the ansers '''
QUESTION = 2

''' State to show the correct answer of the previous question to the players'''
ANSWER = 3

''' Final state of the game. The system shows the leaderboard '''
LEADERBOARD = 4
