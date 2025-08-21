import random

pieceScore = {1:1, 2:3, 3:3, 4:5, 5:8, 6:10, 7:1, 8:3, 9:3, 10:5, 11:8, 12:10, 0:0} 
checkMate = 1000
staleMate = 0
DEPTH = 2

def findRandomMove(validMoves):
    return random.choice(validMoves)

# moves only based on piece values 

def findMinMaxMove(gs, validMoves):
    multi = 1 if gs.whiteToMove else -1
    oppMinMaxScore = checkMate
    bestPlayerMove = None
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        oppMoves = gs.getValidMoves()
        if gs.staleMate:
            oppMaxScore = staleMate
        elif gs.checkMate:
            oppMaxScore = -checkMate
        else:
            oppMaxScore = -checkMate
            for oppMove in oppMoves:
                gs.makeMove(oppMove)
                gs.getValidMoves()
                if gs.checkMate:
                    score = checkMate
                elif gs.staleMate:
                    score = staleMate
                else:
                    score = -multi * pieceEvaluation(gs.board)
                
                if score > oppMaxScore :
                    oppMaxScore = score
                gs.undoMove()
        if oppMaxScore < oppMinMaxScore:
            oppMinMaxScore = oppMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove


def findBestMove(gs, validMoves):
    global nextMove
    nextMove = None
    # findMinMaxMoveRecursive(gs, validMoves, DEPTH, gs.whiteToMove)
    findNegaMaxMove(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    
    return nextMove

def findMinMaxMoveRecursive(gs, validMoves, depth, whiteToMove):
    global nextMove
    
    if depth == 0:
        return pieceEvaluation(gs)
    
    if whiteToMove:
        maxScore = -checkMate
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMinMaxMoveRecursive(gs, nextMoves, depth-1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
            
    else:
        minScore = checkMate
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMinMaxMoveRecursive(gs, nextMoves, depth-1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore
                
def findNegaMaxMove(gs, validMoves, depth, multi):
    global nextMove
    if depth == 0:
        return multi * scoreBoard(gs)
    maxScore = -checkMate
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findNegaMaxMove(gs, nextMoves, depth-1, -multi)
        print(len(validMoves))
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore

def scoreBoard(gs):
    if gs.checkMate :
        if gs.whiteToMove:
            return -checkMate
        else:
            return checkMate
        
    score = 0
    for row in gs.board:
        for square in row:
            if 1 <= square <= 6:
                score += pieceScore[square]
            elif 7 <= square <= 12:
                score -= pieceScore[square]
        
    return score    

def pieceEvaluation(board):
    score = 0
    for row in board:
        for square in row:
            if 1 <= square <= 6:
                score += pieceScore[square]
            elif 7 <= square <= 12:
                score -= pieceScore[square]
        
    return score