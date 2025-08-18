import numpy as np
import chess

class gameState:
    E = 0
    WP, WN, WB, WR, WQ, WK = 1, 2, 3, 4, 5, 6
    BP, BN, BB, BR, BQ, BK = 7, 8, 9, 10, 11 , 12
    
    def __init__(self):
        self.board = np.zeros((8, 8), dtype=np.int8)
        self.board[7] = [self.WR, self.WN, self.WB, self.WQ, self.WK, self.WB, self.WN, self.WR]
        self.board[6] = [self.WP] * 8
        self.board[1] = [self.BP] * 8
        self.board[0] = [self.BR, self.BN, self.BB, self.BQ, self.BK, self.BB, self.BN, self.BR]

        
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.BlaKingLocation = (0,4)

        self.moveFunctionList = [self.getPawnMoves , self.getKnightMoves , self.getBishopMoves ,
                                 self.getRookMoves , self.getQueenMoves , self.getKingMoves , 
                                 self.getPawnMoves , self.getKnightMoves , self.getBishopMoves ,
                                 self.getRookMoves , self.getQueenMoves , self.getKingMoves  ]
        
    
    def makeMove(self , move):
        self.board[move.startRow][move.startCol] = 0
        self.board[move.endRow][move.endCol] = move.moved_piece
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        
        if move.moved_piece == 6:
            self.whiteKingLocation = (move.endRow , move.endCol)
        elif move.moved_piece == 12:
            self.BlaKingLocation = (move.endRow , move.endCol)
        
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.moved_piece
            self.board[move.endRow][move.endCol] = move.captured_piece
            self.whiteToMove = not self.whiteToMove
                    
            if move.moved_piece == 6:
                self.whiteKingLocation = (move.startRow , move.startCol)
            elif move.moved_piece == 12:
                self.BlaKingLocation = (move.startRow , move.startCol)
    
    def getValidMoves(self):
        moves = self.getAllPossibleMoves()
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])        
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        return moves
    
    
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0] , self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.BlaKingLocation[0] , self.BlaKingLocation[1])
    
    def squareUnderAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                self.whiteToMove = not self.whiteToMove
                return True
        self.whiteToMove = not self.whiteToMove
        return False
    
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c]
                if (1 <= turn <= 6 and self.whiteToMove) or (7 <= turn <= 12 and not self.whiteToMove):
                    piece = self.board[r][c]
                    self.moveFunctionList[piece-1](r, c, moves)
            
        return moves
    # Moves checker for all pieces
    
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if r > 0 :
                if self.board[r-1][c] == 0 and r > 0:
                    moves.append(Move((r,c) , (r-1 , c) , self.board))
                    if r == 6 and self.board[r-2][c] == 0:
                        moves.append(Move((r,c) , (r-2 , c) , self.board))
            
            if r-1 >=0 and c-1 >= 0:
                if 6 < self.board[r-1][c-1] < 13:
                    moves.append(Move((r,c) , (r-1 , c-1) , self.board))
            
            if r-1 >= 0 and c+1 <= 7:
                if 6 < self.board[r-1][c+1] < 13:
                    moves.append(Move((r,c) , (r-1 , c+1) , self.board))
                    
            
        else:
            if r < 7:
                if self.board[r+1][c] == 0:
                    moves.append(Move((r,c) , (r+1 , c) , self.board))
                    if r == 1 and self.board[r+2][c] == 0:
                        moves.append(Move((r,c) , (r+2 , c) , self.board)) 
                    
            if r+1 <=7 and c-1 >= 0:
                if 0 < self.board[r+1][c-1] < 7:
                    moves.append(Move((r,c) , (r+1 , c-1) , self.board))
            
            if r+1 <= 7 and c+1 <= 7 :
                if 0 < self.board[r+1][c+1] < 7:
                    moves.append(Move((r,c) , (r+1 , c+1) , self.board))
            
        
        
    # def getKnightMoves(self, r, c, moves):
    #     if self.whiteToMove:
    #         if r-2 >= 0 and c-1 >= 0 :
    #             if self.board[r-2][c-1] == 0 or 6 < self.board[r-2][c-1] < 13 :
    #                 moves.append(Move((r,c) , (r-2 , c-1) , self.board))
            
    #         if r-2 >= 0 and c+1 <= 7 :
    #             if self.board[r-2][c+1] == 0 or 6 < self.board[r-2][c+1] < 13 :
    #                 moves.append(Move((r,c) , (r-2 , c+1) , self.board))
            
    #         if r+2 <= 7 and c-1 >= 0 :
    #             if self.board[r+2][c-1] == 0 or 6 < self.board[r+2][c-1] < 13 :
    #                 moves.append(Move((r,c) , (r+2 , c-1) , self.board))
            
    #         if r+2 <= 7 and c+1 <= 7 :
    #             if self.board[r+2][c+1] == 0 or 6 < self.board[r+2][c+1] < 13 :
    #                 moves.append(Move((r,c) , (r+2 , c+1) , self.board))
            
    #         if r+1 <= 7 and c+2 <= 7 :
    #             if self.board[r+1][c+2] == 0 or 6 < self.board[r+1][c+2] < 13 :
    #                 moves.append(Move((r,c) , (r+1 , c+2) , self.board))
                    
    #         if r+1 <= 7 and c-2 >= 0 :
    #             if self.board[r+1][c-2] == 0 or 6 < self.board[r+1][c-2] < 13 :
    #                 moves.append(Move((r,c) , (r+1 , c-2) , self.board))
                    
    #         if r-1 >= 0 and c+2 <= 7 :
    #             if self.board[r-1][c+2] == 0 or 6 < self.board[r-1][c+2] < 13 :
    #                 moves.append(Move((r,c) , (r-1 , c+2) , self.board))
                    
    #         if r-1 >= 0 and c-2 >= 0 :
    #             if self.board[r-1][c-2] == 0 or 6 < self.board[r-1][c-2] < 13 :
    #                 moves.append(Move((r,c) , (r-1 , c-2) , self.board))
                    
    #     else:
            
    #         if r-2 >= 0 and c-1 >= 0 :
    #             if 0 <= self.board[r-2][c-1] < 7 :
    #                 moves.append(Move((r,c) , (r-2 , c-1) , self.board))
            
    #         if r-2 >= 0 and c+1 <= 7 :
    #             if 0 <= self.board[r-2][c+1] < 7 :
    #                 moves.append(Move((r,c) , (r-2 , c+1) , self.board))
            
    #         if r+2 <= 7 and c-1 >= 0 :
    #             if 0 <= self.board[r+2][c-1] < 7 :
    #                 moves.append(Move((r,c) , (r+2 , c-1) , self.board))
            
    #         if r+2 <= 7 and c+1 <= 7 :
    #             if 0 <= self.board[r+2][c+1] < 7 :
    #                 moves.append(Move((r,c) , (r+2 , c+1) , self.board))
            
    #         if r+1 <= 7 and c+2 <= 7 :
    #             if 0 <= self.board[r+1][c+2] < 7 :
    #                 moves.append(Move((r,c) , (r+1 , c+2) , self.board))
                    
    #         if r+1 <= 7 and c-2 >= 0 :
    #             if 0 <= self.board[r+1][c-2] < 7 :
    #                 moves.append(Move((r,c) , (r+1 , c-2) , self.board))
                    
    #         if r-1 >= 0 and c+2 <= 7 :
    #             if 0 <= self.board[r-1][c+2] < 7 :
    #                 moves.append(Move((r,c) , (r-1 , c+2) , self.board))
                    
    #         if r-1 >= 0 and c-2 >= 0 :
    #             if 0 <= self.board[r-1][c-2] < 7 :
    #                 moves.append(Move((r,c) , (r-1 , c-2) , self.board))
                    
    
    def getKnightMoves(self , r, c, moves):
        direction = [
            (-2, -1), (-2, +1), (+2, -1), (+2, +1),
            (+1, +2), (+1, -2), (-1, +2), (-1, -2)
        ]
        self.generator(r, c, moves, direction)
            
    
    # def getBishopMoves(self, r, c, moves):
    #     if self.whiteToMove:
    #         for i in range(1,8):
    #             if r+i <= 7 and c+i <= 7 :
    #                 if self.board[r+i][c+i] == 0 :
    #                     moves.append(Move((r,c) , (r+i , c+i) , self.board))
    #                 elif  6 < self.board[r+i][c+i] < 13 :
    #                     moves.append(Move((r,c) , (r+i , c+i) , self.board))
    #                 if 0 < self.board[r+i][c+i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r-i <= 7 and c-i <= 7 :
    #                 if self.board[r-i][c-i] == 0 :
    #                     moves.append(Move((r,c) , (r-i , c-i) , self.board))
    #                 elif  6 < self.board[r-i][c-i] < 13 :
    #                     moves.append(Move((r,c) , (r-i , c-i) , self.board))
    #                 if 0 < self.board[r-i][c-i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r+i <= 7 and c-i <= 7 :
    #                 if self.board[r+i][c-i] == 0 :
    #                     moves.append(Move((r,c) , (r+i , c-i) , self.board))
    #                 elif  6 < self.board[r+i][c-i] < 13 :
    #                     moves.append(Move((r,c) , (r+i , c-i) , self.board))
    #                 if 0 < self.board[r+i][c-i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r-i <= 7 and c+i <= 7 :
    #                 if self.board[r-i][c+i] == 0 :
    #                     moves.append(Move((r,c) , (r-i , c+i) , self.board))
    #                 elif  6 < self.board[r-i][c+i] < 13 :
    #                     moves.append(Move((r,c) , (r-i , c+i) , self.board))
    #                 if 0 < self.board[r-i][c+i] < 13 :
    #                     break
                    
    #     else :
    #         for i in range(1,8):
    #             if r+i <= 7 and c+i <= 7 :
    #                 if self.board[r+i][c+i] == 0 :
    #                     moves.append(Move((r,c) , (r+i , c+i) , self.board))
    #                 elif  0 < self.board[r+i][c+i] < 7 :
    #                     moves.append(Move((r,c) , (r+i , c+i) , self.board))
    #                 if 0 < self.board[r+i][c+i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r-i <= 7 and c-i <= 7 :
    #                 if self.board[r-i][c-i] == 0 :
    #                     moves.append(Move((r,c) , (r-i , c-i) , self.board))
    #                 elif  0 < self.board[r-i][c-i] < 7 :
    #                     moves.append(Move((r,c) , (r-i , c-i) , self.board))
    #                 if 0 < self.board[r-i][c-i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r+i <= 7 and c-i <= 7 :
    #                 if self.board[r+i][c-i] == 0 :
    #                     moves.append(Move((r,c) , (r+i , c-i) , self.board))
    #                 elif  0 < self.board[r+i][c-i] < 7 :
    #                     moves.append(Move((r,c) , (r+i , c-i) , self.board))
    #                 if 0 < self.board[r+i][c-i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r-i <= 7 and c+i <= 7 :
    #                 if self.board[r-i][c+i] == 0 :
    #                     moves.append(Move((r,c) , (r-i , c+i) , self.board))
    #                 elif  0 < self.board[r-i][c+i] < 7 :
    #                     moves.append(Move((r,c) , (r-i , c+i) , self.board))
    #                 if 0 < self.board[r-i][c+i] < 13 :
    #                     break
                    

    def getBishopMoves(self, r, c, moves):
        direction = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]    
        self.generator(r, c, moves, direction, 8)
        
        
        
    # def getRookMoves(self, r, c, moves):
    #     if self.whiteToMove:
    #         for i in range(1,8):
    #             if r+i <= 7 :
    #                 if self.board[r+i][c] == 0 :
    #                     moves.append(Move((r,c) , (r+i , c) , self.board))
    #                 elif  6 < self.board[r+i][c] < 13 :
    #                     moves.append(Move((r,c) , (r+i , c) , self.board))
    #                 if 0 < self.board[r+i][c] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r-i >= 0 :
    #                 if self.board[r-i][c] == 0 :
    #                     moves.append(Move((r,c) , (r-i , c) , self.board))
    #                 elif  6 < self.board[r-i][c] < 13 :
    #                     moves.append(Move((r,c) , (r-i , c) , self.board))
    #                 if 0 < self.board[r-i][c] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if c+i <= 7 :
    #                 if self.board[r][c+i] == 0 :
    #                     moves.append(Move((r,c) , (r , c+i) , self.board))
    #                 elif  6 < self.board[r][c+i] < 13 :
    #                     moves.append(Move((r,c) , (r , c+i) , self.board))
    #                 if 0 < self.board[r][c+i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if c-i >= 0 :
    #                 if self.board[r][c-i] == 0 :
    #                     moves.append(Move((r,c) , (r , c-i) , self.board))
    #                 elif  6 < self.board[r][c-i] < 13 :
    #                     moves.append(Move((r,c) , (r , c-i) , self.board))
    #                 if 0 < self.board[r][c-i] < 13 :
    #                     break
                    
    #     else :
            
    #         for i in range(1,8):
    #             if r+i <= 7 :
    #                 if self.board[r+i][c] == 0 :
    #                     moves.append(Move((r,c) , (r+i , c) , self.board))
    #                 elif  0 < self.board[r+i][c] < 7 :
    #                     moves.append(Move((r,c) , (r+i , c) , self.board))
    #                 if 0 < self.board[r+i][c] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r-i >= 0 :
    #                 if self.board[r-i][c] == 0 :
    #                     moves.append(Move((r,c) , (r-i , c) , self.board))
    #                 elif  0 < self.board[r-i][c] < 7 :
    #                     moves.append(Move((r,c) , (r-i , c) , self.board))
    #                 if 0 < self.board[r-i][c] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if c+i <= 7 :
    #                 if self.board[r][c+i] == 0 :
    #                     moves.append(Move((r,c) , (r , c+i) , self.board))
    #                 elif  0 < self.board[r][c+i] < 7 :
    #                     moves.append(Move((r,c) , (r , c+i) , self.board))
    #                 if 0 < self.board[r][c+i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if c-i >= 0 :
    #                 if self.board[r][c-i] == 0 :
    #                     moves.append(Move((r,c) , (r , c-i) , self.board))
    #                 elif  0 < self.board[r][c-i] < 7 :
    #                     moves.append(Move((r,c) , (r , c-i) , self.board))
    #                 if 0 < self.board[r][c-i] < 13 :
    #                     break
                    
                    
    def getRookMoves(self, r, c, moves):
        direction = [(0, -1), (0, +1), (+1, 0), (-1, 0)]    
        self.generator(r, c, moves, direction, 8)
                    
                    
                    
    # def getQueenMoves(self, r, c, moves):
    #     if self.whiteToMove:
    #         for i in range(1,8):
    #             if r+i <= 7 :
    #                 if self.board[r+i][c] == 0 :
    #                     moves.append(Move((r,c) , (r+i , c) , self.board))
    #                 elif  6 < self.board[r+i][c] < 13 :
    #                     moves.append(Move((r,c) , (r+i , c) , self.board))
    #                 if 0 < self.board[r+i][c] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r-i >= 0 :
    #                 if self.board[r-i][c] == 0 :
    #                     moves.append(Move((r,c) , (r-i , c) , self.board))
    #                 elif  6 < self.board[r-i][c] < 13 :
    #                     moves.append(Move((r,c) , (r-i , c) , self.board))
    #                 if 0 < self.board[r-i][c] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if c+i <= 7 :
    #                 if self.board[r][c+i] == 0 :
    #                     moves.append(Move((r,c) , (r , c+i) , self.board))
    #                 elif  6 < self.board[r][c+i] < 13 :
    #                     moves.append(Move((r,c) , (r , c+i) , self.board))
    #                 if 0 < self.board[r][c+i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if c-i >= 0 :
    #                 if self.board[r][c-i] == 0 :
    #                     moves.append(Move((r,c) , (r , c-i) , self.board))
    #                 elif  6 < self.board[r][c-i] < 13 :
    #                     moves.append(Move((r,c) , (r , c-i) , self.board))
    #                 if 0 < self.board[r][c-i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r+i <= 7 and c+i <= 7 :
    #                 if self.board[r+i][c+i] == 0 :
    #                     moves.append(Move((r,c) , (r+i , c+i) , self.board))
    #                 elif  6 < self.board[r+i][c+i] < 13 :
    #                     moves.append(Move((r,c) , (r+i , c+i) , self.board))
    #                 if 0 < self.board[r+i][c+i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r-i <= 7 and c-i <= 7 :
    #                 if self.board[r-i][c-i] == 0 :
    #                     moves.append(Move((r,c) , (r-i , c-i) , self.board))
    #                 elif  6 < self.board[r-i][c-i] < 13 :
    #                     moves.append(Move((r,c) , (r-i , c-i) , self.board))
    #                 if 0 < self.board[r-i][c-i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r+i <= 7 and c-i <= 7 :
    #                 if self.board[r+i][c-i] == 0 :
    #                     moves.append(Move((r,c) , (r+i , c-i) , self.board))
    #                 elif  6 < self.board[r+i][c-i] < 13 :
    #                     moves.append(Move((r,c) , (r+i , c-i) , self.board))
    #                 if 0 < self.board[r+i][c-i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r-i <= 7 and c+i <= 7 :
    #                 if self.board[r-i][c+i] == 0 :
    #                     moves.append(Move((r,c) , (r-i , c+i) , self.board))
    #                 elif  6 < self.board[r-i][c+i] < 13 :
    #                     moves.append(Move((r,c) , (r-i , c+i) , self.board))
    #                 if 0 < self.board[r-i][c+i] < 13 :
    #                     break

    #     else :
            
            
    #         for i in range(1,8):
    #             if r+i <= 7 :
    #                 if self.board[r+i][c] == 0 :
    #                     moves.append(Move((r,c) , (r+i , c) , self.board))
    #                 elif  0 < self.board[r+i][c] < 7:
    #                     moves.append(Move((r,c) , (r+i , c) , self.board))
    #                 if 0 < self.board[r+i][c] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r-i >= 0 :
    #                 if self.board[r-i][c] == 0 :
    #                     moves.append(Move((r,c) , (r-i , c) , self.board))
    #                 elif  0 < self.board[r-i][c] < 7:
    #                     moves.append(Move((r,c) , (r-i , c) , self.board))
    #                 if 0 < self.board[r-i][c] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if c+i <= 7 :
    #                 if self.board[r][c+i] == 0 :
    #                     moves.append(Move((r,c) , (r , c+i) , self.board))
    #                 elif  0 < self.board[r][c+i] < 7:
    #                     moves.append(Move((r,c) , (r , c+i) , self.board))
    #                 if 0 < self.board[r][c+i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if c-i >= 0 :
    #                 if self.board[r][c-i] == 0 :
    #                     moves.append(Move((r,c) , (r , c-i) , self.board))
    #                 elif  0 < self.board[r][c-i] < 7:
    #                     moves.append(Move((r,c) , (r , c-i) , self.board))
    #                 if 0 < self.board[r][c-i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r+i <= 7 and c+i <= 7 :
    #                 if self.board[r+i][c+i] == 0 :
    #                     moves.append(Move((r,c) , (r+i , c+i) , self.board))
    #                 elif  0 < self.board[r+i][c+i] < 7 :
    #                     moves.append(Move((r,c) , (r+i , c+i) , self.board))
    #                 if 0 < self.board[r+i][c+i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r-i <= 7 and c-i <= 7 :
    #                 if self.board[r-i][c-i] == 0 :
    #                     moves.append(Move((r,c) , (r-i , c-i) , self.board))
    #                 elif  0 < self.board[r-i][c-i] < 7 :
    #                     moves.append(Move((r,c) , (r-i , c-i) , self.board))
    #                 if 0 < self.board[r-i][c-i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r+i <= 7 and c-i <= 7 :
    #                 if self.board[r+i][c-i] == 0 :
    #                     moves.append(Move((r,c) , (r+i , c-i) , self.board))
    #                 elif  0 < self.board[r+i][c-i] < 7 :
    #                     moves.append(Move((r,c) , (r+i , c-i) , self.board))
    #                 if 0 < self.board[r+i][c-i] < 13 :
    #                     break
                    
    #         for i in range(1,8):
    #             if r-i <= 7 and c+i <= 7 :
    #                 if self.board[r-i][c+i] == 0 :
    #                     moves.append(Move((r,c) , (r-i , c+i) , self.board))
    #                 elif  0 < self.board[r-i][c+i] < 7 :
    #                     moves.append(Move((r,c) , (r-i , c+i) , self.board))
    #                 if 0 < self.board[r-i][c+i] < 13 :
    #                     break


    def getQueenMoves(self, r, c, moves):
        direction = [(0, -1), (0, +1), (+1, 0), (-1, 0), 
                     (-1, -1), (-1, +1), (+1, -1), (+1, +1)]   
        self.generator(r, c, moves, direction, 8)
        

    def getKingMoves(self, r, c, moves):
        direction = [(-1,-1) , (-1,0) , (-1,+1) , (0,+1) , 
                     (+1,+1) , (+1,0) , (+1,-1) , (0,-1)]
        self.generator(r, c, moves, direction)
        
        
            
    def generator(self, r, c, moves, direction , n=2):
        
        for dr , dc in direction:
            for i in range(1,n):
                endR , endC = r + dr*i , c + dc*i
                if 0 <= endR <= 7 and 0 <= endC <= 7:
                    targetPos = self.board[endR][endC]
                    if targetPos == 0 :
                        moves.append(Move((r, c), (endR, endC), self.board)) 
                    else:
                        if self.whiteToMove:
                            if 7 <= targetPos <= 12: 
                                moves.append(Move((r, c), (endR, endC), self.board))
                        else:
                            if 1 <= targetPos <= 6: 
                                moves.append(Move((r, c), (endR, endC), self.board))
                        break
                else:
                    break 

        
class Move():
    
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    
    def __init__(self , start , end , board):
        self.startRow = start[0]
        self.startCol = start[1]
        self.endRow = end[0]
        self.endCol = end[1]
        self.moved_piece = board[self.startRow][self.startCol]
        self.captured_piece = board[self.endRow][self.endCol]
        self.MoveId = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol
        
    def __eq__(self, other):
        if isinstance(other , Move):
            return self.MoveId == other.MoveId
        return False
    
    

    def getRankFile(self , r , c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
    
    def getChessNotation(self):
        return self.getRankFile(self.startRow , self.startCol) + self.getRankFile(self.endRow , self.endCol)