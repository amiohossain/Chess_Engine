import random

pieceScore = {1:1, 2:3, 3:3, 4:5, 5:8, 6:10, 7:1, 8:3, 9:3, 10:5, 11:8, 12:10, 0:0} 
checkMate = 1000
staleMate = 0

def findRandomMove(validMoves):
    return random.choice(validMoves)

# moves only based on piece values 

def findProfitableMove(gs, validMoves):
    multi = 1 if gs.whiteToMove else -1
    oppMinMaxScore = checkMate
    bestPlayerMove = None
    
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        oppMoves = gs.getValidMoves()
        oppMaxScore = -checkMate
        for oppMove in oppMoves:
            gs.makeMove(oppMove)
            if gs.checkMate:
                score = -multi * checkMate
            elif gs.staleMate:
                score = staleMate
            else:
                score = -multi * pieceEvaluation(gs.board)
            
            if score > oppMaxScore :
                oppMaxScore = score
            gs.undoMove()
        if oppMaxScore > oppMinMaxScore:
            oppMinMaxScore = oppMaxScore
        gs.undoMove()
    return bestPlayerMove


def pieceEvaluation(board):
    score = 0
    for row in board:
        for square in row:
            if 1 <= square <= 6:
                score += pieceScore[square]
            elif 7 <= square <= 12:
                score -= pieceScore[square]
        
    return score