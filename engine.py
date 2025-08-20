import numpy as np

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
        self.captured = 0
        self.capturedWhite = []
        self.capturedBlack = []

        self.whiteKingLocation = (7,4)
        self.BlaKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False
        self.enPassentMove = ()
        
        self.currentCastlingRights = CasstleRights(True, True, True, True)
        self.castlingRightsLogs = [CasstleRights(self.currentCastlingRights.wks , self.currentCastlingRights.bks,
                                                 self.currentCastlingRights.wqs , self.currentCastlingRights.bqs)]
        
        self.moveFunctionList = [self.getPawnMoves , self.getKnightMoves , self.getBishopMoves ,
                                 self.getRookMoves , self.getQueenMoves , self.getKingMoves , 
                                 self.getPawnMoves , self.getKnightMoves , self.getBishopMoves ,
                                 self.getRookMoves , self.getQueenMoves , self.getKingMoves  ]
        
    
    def makeMove(self , move):
        self.board[move.startRow][move.startCol] = 0
        self.board[move.endRow][move.endCol] = move.movedPiece
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        
        if move.movedPiece == 6:
            self.whiteKingLocation = (move.endRow , move.endCol)
        elif move.movedPiece == 12:
            self.BlaKingLocation = (move.endRow , move.endCol)
            
        if move.isPawnPromotion:
            if move.movedPiece == 1:
                self.board[move.endRow][move.endCol] = 5
            elif move.movedPiece == 7:
                self.board[move.endRow][move.endCol] = 11
                
        if move.isEnPassentMove:
            self.board[move.startRow][move.endCol] = 0
            
        if (move.movedPiece == 1 or move.movedPiece == 7) and (abs(move.startRow - move.endRow) == 2):
            self.enPassentMove = ((move.startRow + move.endRow)//2 , move.startCol)
        else: self.enPassentMove = ()
        
        
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = 0
            else:
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = 0
                

        
        # if move.isCapture:
        #     if move.isEnPassentMove:
        #         captured = 1 if move.movedPiece == 7 else 7
        #     else:
        #         captured = move.capturedPiece

        #     if captured <= 6:
        #         self.capturedWhite.append(captured)
        #     else:
        #         self.capturedBlack.append(captured)

        #     print(self.capturedBlack, self.capturedWhite)





        
        self.updateCastlingRights(move)
        self.castlingRightsLogs.append(CasstleRights(self.currentCastlingRights.wks , self.currentCastlingRights.bks,
                                                 self.currentCastlingRights.wqs , self.currentCastlingRights.bqs)) 
        
        
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.movedPiece
            self.board[move.endRow][move.endCol] = move.capturedPiece
            self.whiteToMove = not self.whiteToMove
                    
            if move.movedPiece == 6:
                self.whiteKingLocation = (move.startRow , move.startCol)
            elif move.movedPiece == 12:
                self.BlaKingLocation = (move.startRow , move.startCol)
                
            if move.isEnPassentMove:
                self.board[move.endRow][move.endCol] = 0
                self.board[move.startRow][move.endCol] = move.capturedPiece
                self.enPassentMove = (move.endRow , move.endCol)
                
            if (move.movedPiece == 1 or move.movedPiece == 7) and (abs(move.startRow - move.endRow) == 2):
                self.enPassentMove = ()
        
            self.castlingRightsLogs.pop()
            self.currentCastlingRights = CasstleRights(
                                            self.castlingRightsLogs[-1].wks,
                                            self.castlingRightsLogs[-1].bks,
                                            self.castlingRightsLogs[-1].wqs,
                                            self.castlingRightsLogs[-1].bqs
                                        )
            
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = 0
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = 0

            self.checkMate = False
            self.staleMate = False
    
    def getValidMoves(self):
        tempEnPassent = self.enPassentMove
        tempCastleRights = CasstleRights(self.currentCastlingRights.wks , self.currentCastlingRights.bks,
                                            self.currentCastlingRights.wqs , self.currentCastlingRights.bqs)
        
        moves = self.getAllPossibleMoves()
        
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0] , self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.BlaKingLocation[0] , self.BlaKingLocation[1], moves)
            
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])        
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0 :
            if self.inCheck(): 
                self.checkMate = True
            else : 
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
            
        self.enPassentMove = tempEnPassent
        self.currentCastlingRights = tempCastleRights
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
                elif ((r-1,c-1) == self.enPassentMove):
                    moves.append(Move((r,c) , (r-1 , c-1) , self.board , enPassentPossible=True))
            
            if r-1 >= 0 and c+1 <= 7:
                if 6 < self.board[r-1][c+1] < 13:
                    moves.append(Move((r,c) , (r-1 , c+1) , self.board))
                elif ((r-1,c+1) == self.enPassentMove):
                    moves.append(Move((r,c) , (r-1 , c+1) , self.board , enPassentPossible=True))
                    
            
        else:
            if r < 7:
                if self.board[r+1][c] == 0:
                    moves.append(Move((r,c) , (r+1 , c) , self.board))
                    if r == 1 and self.board[r+2][c] == 0:
                        moves.append(Move((r,c) , (r+2 , c) , self.board)) 
                    
            if r+1 <=7 and c-1 >= 0:
                if 0 < self.board[r+1][c-1] < 7:
                    moves.append(Move((r,c) , (r+1 , c-1) , self.board))
                elif ((r+1,c-1) == self.enPassentMove):
                    moves.append(Move((r,c) , (r+1 , c-1) , self.board , enPassentPossible=True))
            
            if r+1 <= 7 and c+1 <= 7 :
                if 0 < self.board[r+1][c+1] < 7:
                    moves.append(Move((r,c) , (r+1 , c+1) , self.board))
                elif ((r+1,c+1) == self.enPassentMove):
                    moves.append(Move((r,c) , (r+1 , c+1) , self.board , enPassentPossible=True)) 
                    
    def getKnightMoves(self , r, c, moves):
        direction = [
            (-2, -1), (-2, +1), (+2, -1), (+2, +1),
            (+1, +2), (+1, -2), (-1, +2), (-1, -2)
        ]
        self.generator(r, c, moves, direction)
        
    def getBishopMoves(self, r, c, moves):
        direction = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]    
        self.generator(r, c, moves, direction, 8)
                           
    def getRookMoves(self, r, c, moves):
        direction = [(0, -1), (0, +1), (+1, 0), (-1, 0)]    
        self.generator(r, c, moves, direction, 8)

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

                
    def updateCastlingRights(self, move):
        if move.movedPiece == 6:
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.movedPiece == 12:
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.movedPiece == 4 :
            if move.startCol == 0:
                self.currentCastlingRights.wqs = False
            elif move.startCol == 7:
                self.currentCastlingRights.wks = False
        elif move.movedPiece == 10:
            if move.startCol == 0:
                self.currentCastlingRights.bqs = False
            elif move.startCol == 7:
                self.currentCastlingRights.bks = False
                
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(r, c, moves)
        
    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == 0 and self.board[r][c+2] == 0:
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove = True ))
    
    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == 0 and self.board[r][c-2] == 0 and self.board[r][c-3] == 0:
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))

    

class CasstleRights():
    def __init__(self , wks , bks , wqs , bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

        
class Move():
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self , start , end , board , enPassentPossible = False, isCastleMove = False):
        self.startRow = start[0]
        self.startCol = start[1]
        self.endRow = end[0]
        self.endCol = end[1]
        self.movedPiece = (board[self.startRow][self.startCol])
        self.capturedPiece = (board[self.endRow][self.endCol])


        self.isPawnPromotion =  ((self.movedPiece == 1 and self.endRow == 0) or (self.movedPiece == 7 and self.endRow == 7)) 

        self.isEnPassentMove = enPassentPossible
        if self.isEnPassentMove:
            self.capturedPiece = 1 if self.movedPiece == 7 else 7
            
        self.isCastleMove = isCastleMove
        
        self.MoveId = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol
        # self.isCapture = (self.capturedPiece != 0) or self.isEnPassentMove
        
        self.piece_names = {1:"White Pawn", 2:"White Knight", 3:"White Bishop", 4:"White Rook", 5:"White Queen", 6:"White King",
                   7:"Black Pawn", 8:"Black Knight", 9:"Black Bishop", 10:"Black Rook", 11:"Black Queen", 12:"Black King",
                   0:"Nothing"} 
        
    def __eq__(self, other):
        if isinstance(other , Move):
            return self.MoveId == other.MoveId
        return False

    def getRankFile(self , r , c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
    
    def getChessNotation(self):
        return f"{self.piece_names[self.movedPiece]} moved from {self.getRankFile(self.startRow , self.startCol)} to {self.getRankFile(self.endRow , self.endCol)} Capturing {self.piece_names[self.capturedPiece]}"