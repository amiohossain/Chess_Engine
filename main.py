import pygame as p
import engine

width = height = 512
dimension = 8
sq_size = height//dimension
max_fps = 15
images = {} #Stores Image
selected = () #Selected Square
clicked = [] 


#Image Loader
def load_img():
    pieces = list(range(1,13))
    for piece in pieces:
        images[str(piece)] = p.transform.scale(p.image.load(f"./images/{str(piece)}.png") , (sq_size , sq_size))
        
def main():
    global selected ,clicked
    
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
                if selected == (row , col):
                    selected = ()
                    clicked = []
                else:
                    selected = (row , col)
                    clicked.append(selected)
                if len(clicked) == 2:
                    move = engine.Move(clicked[0] , clicked[1] , gs.board)
                    if move in validMoves:
                        gs.makeMove(move)
                        moveMade = True
                        selected = ()
                        clicked = []
                        print(move.getChessNotation())
                    else:
                        clicked = [selected]
            elif e.type == p.KEYDOWN :
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
        if moveMade :
            validMoves = gs.getValidMoves()
            moveMade = False
        drawGameState(scrn , gs)
        clk.tick(max_fps)
        p.display.flip()
        
def drawGameState(scrn , gs):
   drawBoard(scrn)
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