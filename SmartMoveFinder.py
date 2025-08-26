import random
import time 

pieceScore = {1:1, 2:3, 3:3, 4:5, 5:8, 6:10, 7:1, 8:3, 9:3, 10:5, 11:8, 12:10, 0:0} 
checkMate = 1000
staleMate = 0
DEPTH = 25
counter = 0

def findRandomMove(validMoves):
    return random.choice(validMoves)


import time

def findBestMove(gs, validMoves, maxDepth=3, timeLimit=None):
    """
    Finds the best move for the current player with iterative deepening.
    Prints depth and best move at each iteration.
    """
    global nextMove
    nextMove = None
    startTime = time.time()
    
    for depth in range(1, maxDepth + 1):
        print(f"Searching at depth: {depth}")
        findNegaMaxMoveAlphaBeta(gs, validMoves, depth, -checkMate, checkMate,
                                 1 if gs.whiteToMove else -1, depth, startTime, timeLimit)
        
        if nextMove:
            print(f"Depth {depth}: Best move so far -> {nextMove.getChessNotation()}")
        
        if timeLimit and time.time() - startTime > timeLimit:
            print("Time limit reached, stopping search.")
            break
            
    return nextMove


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
    global nextMove , counter
    counter+=1
    if depth == 0:
        return multi * scoreBoard(gs)
    maxScore = -checkMate
    print(depth)
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findNegaMaxMove(gs, nextMoves, depth-1, -multi)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    print(counter)
    return maxScore

def findNegaMaxMoveAlphaBeta(gs, validMoves, depth, alpha, beta, multi, rootDepth, startTime=None, timeLimit=None):
    """
    Alpha-beta pruning negamax search.
    
    gs         : gameState
    validMoves : list of moves at current node
    depth      : remaining depth
    alpha, beta: alpha-beta bounds
    multi      : +1 for white, -1 for black
    rootDepth  : depth at root node (to update nextMove)
    startTime  : optional start time for time control
    timeLimit  : optional time limit in seconds
    """
    global nextMove, counter
    counter += 1

    # Time check
    if startTime and timeLimit:
        if time.time() - startTime > timeLimit:
            return 0  # Return a neutral score if out of time

    if depth == 0:
        return multi * scoreBoard(gs)

    maxScore = -checkMate
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findNegaMaxMoveAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -multi,
                                          rootDepth, startTime, timeLimit)
        gs.undoMove()

        if score > maxScore:
            maxScore = score
            if depth == rootDepth:  # Update nextMove only at root
                nextMove = move

        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break

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