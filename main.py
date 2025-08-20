import pygame as p
import engine

width = height = 512
dimension = 8
sq_size = height//dimension
max_fps = 15
images = {} #Stores Image
sqSelected = () #Selected Square
sqClicked = [] 


#Image Loader
def load_img():
    pieces = list(range(1,13))
    for piece in pieces:
        images[str(piece)] = p.transform.scale(p.image.load(f"./images/{str(piece)}.png") , (sq_size , sq_size))
        
def main():
    global sqSelected ,sqClicked
    
    #Screen Initializer 
    p.init()
    scrn = p.display.set_mode((width , height))
    clk = p.time.Clock()
    scrn.fill(p.Color("white"))

    #Engine Initializer
    gs = engine.gameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    
    #Window Keeper
    load_img()
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                loc = p.mouse.get_pos()
                row = loc[1]//sq_size
                col = loc[0]//sq_size
                if sqSelected == (row , col):
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
                            print(move.getChessNotation())
                    if not moveMade:
                        sqClicked = [sqSelected] 
            elif e.type == p.KEYDOWN :
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
        if moveMade :
            validMoves = gs.getValidMoves()
            moveMade = False
        drawGameState(scrn , gs, validMoves, sqSelected)
        clk.tick(max_fps)
        p.display.flip()
        
        
def highlightSquares(screen , gs, validMoves, sqSelected):
    if sqSelected != ():
        r,c = sqSelected
        if (gs.whiteToMove and (1 <= gs.board[r][c] <= 6)) or ((not gs.whiteToMove) and (7 <= gs.boad[r][c] <= 12)):
            s = p.Surface((sq_size,sq_size))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (c*sq_size,r*sq_size))
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*sq_size, move.endRow*sq_size))
                    
        
def drawGameState(scrn , gs, validMoves, sqSelected):
   drawBoard(scrn)
   highlightSquares(scrn, gs, validMoves, sqSelected)
   drawPiece(scrn,gs.board)
   
def drawBoard(scrn):
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

if __name__ == "__main__":
    main()