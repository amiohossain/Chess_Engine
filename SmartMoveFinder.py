import random

pieceScore = {1:1, 2:3, 3:3, 4:5, 5:8, 6:10, 7:1, 8:3, 9:3, 10:5, 11:8, 12:10, 0:0} 
checkMate = 1000
staleMate = 0

def findRandomMove(validMoves):
    return random.choice(validMoves)

# moves only based on piece values 

def findBestMove(gs, validMoves):
    multi = 1 if gs.whiteToMove else -1
    maxScore = -checkMate
    bestMove = None
    
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        if gs.checkMate:
            score = checkMate
        elif gs.staleMate:
            score = staleMate
        else:
            score = multi * pieceEvaluation(gs.board)
        
        if score > maxScore :
            maxScore = score
            bestMove = playerMove
        gs.undoMove()
    return bestMove


def pieceEvaluation(board):
    score = 0
    for row in board:
        for square in row:
            if 1 <= square <= 6:
                score += pieceScore[square]
            elif 7 <= square <= 12:
                score -= pieceScore[square]
        
    return score