import pygame as p
import engine
import SmartMoveFinder

boardWidth = boardHeight = 512
moveLogPanelWidth, moveLogPanelHeight = 250, boardHeight 
dimension = 8
sq_size = boardHeight//dimension
max_fps = 15
animate = True

images = {} #Stores Image
sqSelected = () #Selected Square
sqClicked = [] 

playerOne = True
playerTwo = False
gameOver = False

# Image Loader
def load_img():
    pieces = list(range(1,13))
    for piece in pieces:
        images[str(piece)] = p.transform.scale(p.image.load(f"./images/{str(piece)}.png") , (sq_size , sq_size))
        
def main():
    global sqSelected ,sqClicked, animate, gameOver
    
    # Screen Initializer 
    p.init()
    scrn = p.display.set_mode((boardWidth + moveLogPanelWidth, boardHeight ))
    clk = p.time.Clock()
    scrn.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 15, False, False)


    # Engine Initializer
    gs = engine.gameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    
    # Window Keeper
    load_img()
    running = True
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    loc = p.mouse.get_pos()
                    row = loc[1]//sq_size
                    col = loc[0]//sq_size
                    if sqSelected == (row , col) or col >= 8:
                        sqSelected = ()
                        sqClicked = []
                    else:
                        sqSelected = (row , col)
                        sqClicked.append(sqSelected)
                    if len(sqClicked) == 2:
                        move = engine.Move(sqClicked[0] , sqClicked[1] , gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                sqSelected = ()
                                sqClicked = []
                        if not moveMade:
                            sqClicked = [sqSelected] 
                        else:
                            print(move.getChessNotation())
            elif e.type == p.KEYDOWN :
                if e.key == p.K_z :
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                elif e.key == p.K_r :
                    gs = engine.gameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    sqClicked = [] 
                    moveMade = False
                    animate = True
                    gameOver = False
                    
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findBestMove(gs, validMoves)
            if AIMove == None:
                AIMove = SmartMoveFinder.findRandomMove(validMoves)
            # AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True                    
                    
        if moveMade :
            if animate:
                animateMove(gs.moveLog[-1], scrn, gs.board, clk)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = True
            
        drawGameState(scrn , gs, validMoves, sqSelected, moveLogFont)

        if gs.checkMate or gs.staleMate:
            gameOver = True
            text = ''
            if gs.staleMate:
                test =  "Stalemate"
            else:
                if gs.whiteToMove:
                    text = "Black wins by Check Mate"
                else:
                    text = "White wins by Check Mate"
            drawEndGameText(text)
          
                
        clk.tick(max_fps)
        p.display.flip()


def highlightSquares(scrn , gs, validMoves, sqSelected):
    if sqSelected != ():
        r,c = sqSelected
        if (gs.whiteToMove and (1 <= gs.board[r][c] <= 6)) or ((not gs.whiteToMove) and (7 <= gs.board[r][c] <= 12)):
            s = p.Surface((sq_size,sq_size))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            scrn.blit(s, (c*sq_size,r*sq_size))
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    scrn.blit(s, (move.endCol*sq_size, move.endRow*sq_size))
                    
        
def drawGameState(scrn , gs, validMoves, sqSelected, moveLogFont):
   drawBoard(scrn)
   highlightSquares(scrn, gs, validMoves, sqSelected)
   drawPiece(scrn,gs.board)
   drawMoveLog(scrn, gs, moveLogFont )
   

   
def drawBoard(scrn):
    global colors
    colors = [p.Color("white") , p.Color("teal")]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r+c)%2)]
            p.draw.rect(scrn , color , p.Rect(c*sq_size , r*sq_size , sq_size , sq_size))

            
def drawPiece(scrn , board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != 0:
                scrn.blit(images[str(piece)] , p.Rect(c*sq_size , r*sq_size , sq_size , sq_size))

def drawMoveLog(scrn, gs, font):
    moveLogRect = p.Rect(boardWidth, 0, moveLogPanelWidth, moveLogPanelHeight)
    p.draw.rect(scrn, p.Color('black'), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    
    for i in range(0, len(moveLog), 2):
        moveString = f"{i//2 +1}. {moveLog[i].getChessNotation()} "
        if i+1 < len(moveLog):
            moveString += moveLog[i+1].getChessNotation()
        moveTexts.append(moveString)
    
    movePerRow = 3
    textY = 5
    for i in range(0, len(moveTexts), movePerRow):
        text = ""
        for j in range(movePerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, 0, p.Color("gray"))
        textLocation = moveLogRect.move(5, textY)
        scrn.blit(textObject, textLocation)
        textY += textObject.get_height() + 2

    


def animateMove(move, scrn, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framePerSq = 10
    #frameCnt = (abs(dR)+abs(dC))*framePerSq
    frameCnt = 5
    
    captured_piece = move.capturedPiece
    en_passant_row = -1
    for frame in range(frameCnt+1):
        r, c = (move.startRow + dR*frame/frameCnt, move.startCol + dC*frame/frameCnt)
        drawBoard(scrn)
        drawPiece(scrn, board)
        color = colors[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol*sq_size, move.endRow*sq_size, sq_size, sq_size)
        p.draw.rect(scrn, color, endSquare)
        # if move.capturedPiece != 0:
        #     if move.isEnPassentPossible:
        #         enPassantRow = move.endRow + 1  if move.capturedPiece == 7 else move.endRow - 1
        #         endSquare = p.Rect(move.endCol * sq_size, enPassantRow * sq_size, sq_size, sq_size )
        #     scrn.blit(images[str(move.movedPiece)], endSquare)
        scrn.blit(images[str(move.movedPiece)], p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))
        p.display.flip()
        clock.tick(60)
        
def drawEndGameText(scrn, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color("gray"))
    textLocation = p.Rect(0, 0, boardWidth, boardHeight).move(boardWidth/2 - textObject.get_width()/2, boardHeight/2 - textObject.get_height()/2)
    scrn.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    scrn.blit(textObject, textLocation.move(2,2))
    
if __name__ == "__main__":
    main()