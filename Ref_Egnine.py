import numpy as np

WHITE, BLACK = True, False

class GameState:
    # Piece IDs
    E = 0
    WP, WN, WB, WR, WQ, WK = 1, 2, 3, 4, 5, 6
    BP, BN, BB, BR, BQ, BK = 7, 8, 9, 10, 11, 12

    # Directions
    KNIGHT_DIRS = [(-2,-1), (-2,1), (2,-1), (2,1), (1,2), (1,-2), (-1,2), (-1,-2)]
    KING_DIRS   = [(-1,-1), (-1,0), (-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1)]
    ROOK_DIRS   = [(0,-1), (0,1), (1,0), (-1,0)]
    BISHOP_DIRS = [(-1,-1), (-1,1), (1,-1), (1,1)]
    QUEEN_DIRS  = ROOK_DIRS + BISHOP_DIRS

    def __init__(self):
        self.board = np.zeros((8, 8), dtype=np.int8)
        # Initial placement
        self.board[7] = [self.WR, self.WN, self.WB, self.WQ, self.WK, self.WB, self.WN, self.WR]
        self.board[6] = [self.WP] * 8
        self.board[1] = [self.BP] * 8
        self.board[0] = [self.BR, self.BN, self.BB, self.BQ, self.BK, self.BB, self.BN, self.BR]

        self.whiteToMove = True
        self.moveLog = []

        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        # Castling rights: (wk, wq, bk, bq)
        self.castlingRights = [True, True, True, True]
        # Track rook/king movement to update rights
        self.moved = {
            ('W','K'): False, ('W','R','a'): False, ('W','R','h'): False,
            ('B','K'): False, ('B','R','a'): False, ('B','R','h'): False
        }

        # En passant target square (row, col) or None
        self.enPassant = None

        # Piece → generator mapping
        self.moveFn = {
            self.WP: self._pawn_moves, self.BP: self._pawn_moves,
            self.WN: self._knight_moves, self.BN: self._knight_moves,
            self.WB: self._bishop_moves, self.BB: self._bishop_moves,
            self.WR: self._rook_moves,   self.BR: self._rook_moves,
            self.WQ: self._queen_moves,  self.BQ: self._queen_moves,
            self.WK: self._king_moves,   self.BK: self._king_moves,
        }

    # -------------------- Helpers --------------------
    @staticmethod
    def _in_bounds(r, c): return 0 <= r < 8 and 0 <= c < 8
    @staticmethod
    def _is_white(piece): return 1 <= piece <= 6
    @staticmethod
    def _is_black(piece): return 7 <= piece <= 12

    def _my_color(self): return WHITE if self.whiteToMove else BLACK
    def _enemy_color(self): return not self._my_color()

    def _king_pos(self, color):
        return self.whiteKingLocation if color == WHITE else self.blackKingLocation

    # -------------------- Move application --------------------
    def makeMove(self, move):
        sr, sc, er, ec = move.startRow, move.startCol, move.endRow, move.endCol
        piece = self.board[sr][sc]
        capture = self.board[er][ec]

        # Move piece
        self.board[sr][sc] = 0
        self.board[er][ec] = piece

        # En passant capture
        if move.is_en_passant:
            if self._is_white(piece):
                self.board[er+1][ec] = 0
            else:
                self.board[er-1][ec] = 0

        # Promotion
        if move.is_promotion:
            self.board[er][ec] = self.WQ if self._is_white(piece) else self.BQ

        # Castling: move rook
        if move.is_castle:
            if ec == 6:  # king-side
                self.board[er][5] = self.board[er][7]
                self.board[er][7] = 0
            else:        # queen-side
                self.board[er][3] = self.board[er][0]
                self.board[er][0] = 0

        # Update king locations
        if piece == self.WK: self.whiteKingLocation = (er, ec)
        if piece == self.BK: self.blackKingLocation = (er, ec)

        # Update castling rights by movement
        self._update_castling_rights_on_move(sr, sc, piece)

        # Update en passant square
        self.enPassant = None
        if piece in (self.WP, self.BP) and abs(er - sr) == 2:
            mid = (sr + er)//2
            self.enPassant = (mid, ec)

        move.moved_piece = piece
        move.captured_piece = capture
        move.prev_en_passant = move.prev_en_passant if hasattr(move, 'prev_en_passant') else None
        move.prev_castle_rights = tuple(self.castlingRights)
        move.prev_en_passant = move.prev_en_passant or self.enPassant

        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    def undoMove(self):
        if not self.moveLog:
            return
        move = self.moveLog.pop()
        sr, sc, er, ec = move.startRow, move.startCol, move.endRow, move.endCol
        piece = move.moved_piece

        # Undo move piece
        self.board[sr][sc] = piece
        self.board[er][ec] = move.captured_piece

        # Undo en passant capture
        if move.is_en_passant:
            if self._is_white(piece):
                self.board[er+1][ec] = self.BP
            else:
                self.board[er-1][ec] = self.WP
            self.board[er][ec] = 0  # landing square was empty originally

        # Undo promotion
        if move.is_promotion:
            self.board[sr][sc] = self.WP if self._is_white(piece) else self.BP

        # Undo castling rook move
        if move.is_castle:
            if ec == 6:  # king-side
                self.board[er][7] = self.board[er][5]
                self.board[er][5] = 0
            else:        # queen-side
                self.board[er][0] = self.board[er][3]
                self.board[er][3] = 0

        # Restore king positions
        if piece == self.WK: self.whiteKingLocation = (sr, sc)
        if piece == self.BK: self.blackKingLocation = (sr, sc)

        # Restore rights/en passant
        self.castlingRights = list(move.prev_castle_rights)
        self.enPassant = move.prev_en_passant

        self.whiteToMove = not self.whiteToMove

    def _update_castling_rights_on_move(self, sr, sc, piece):
        # White side
        if piece == self.WK:
            self.castlingRights[0] = False  # wk
            self.castlingRights[1] = False  # wq
        elif piece == self.WR:
            if (sr, sc) == (7, 0): self.castlingRights[1] = False
            if (sr, sc) == (7, 7): self.castlingRights[0] = False

        # Black side
        if piece == self.BK:
            self.castlingRights[2] = False  # bk
            self.castlingRights[3] = False  # bq
        elif piece == self.BR:
            if (sr, sc) == (0, 0): self.castlingRights[3] = False
            if (sr, sc) == (0, 7): self.castlingRights[2] = False

        # If a rook is captured on its original square, update too
        # (handled implicitly in generation by rights; optional extra here)

    # -------------------- Attack & legality --------------------
    def is_square_attacked(self, r, c, by_color):
        """Fast attack test without generating full move lists."""
        enemy_is_white = (by_color == WHITE)

        # Pawns
        pawn_dirs = [(-1,-1), (-1,1)] if enemy_is_white else [(1,-1), (1,1)]
        for dr, dc in pawn_dirs:
            rr, cc = r+dr, c+dc
            if self._in_bounds(rr, cc):
                p = self.board[rr][cc]
                if enemy_is_white and p == self.WP: return True
                if not enemy_is_white and p == self.BP: return True

        # Knights
        for dr, dc in self.KNIGHT_DIRS:
            rr, cc = r+dr, c+dc
            if self._in_bounds(rr, cc):
                p = self.board[rr][cc]
                if enemy_is_white and p == self.WN: return True
                if not enemy_is_white and p == self.BN: return True

        # Kings (for adjacency checks)
        for dr, dc in self.KING_DIRS:
            rr, cc = r+dr, c+dc
            if self._in_bounds(rr, cc):
                p = self.board[rr][cc]
                if enemy_is_white and p == self.WK: return True
                if not enemy_is_white and p == self.BK: return True

        # Sliding pieces: rooks/queens and bishops/queens
        # Rook-like
        for dr, dc in self.ROOK_DIRS:
            rr, cc = r+dr, c+dc
            while self._in_bounds(rr, cc):
                p = self.board[rr][cc]
                if p != 0:
                    if enemy_is_white and (p == self.WR or p == self.WQ): return True
                    if not enemy_is_white and (p == self.BR or p == self.BQ): return True
                    break
                rr += dr; cc += dc

        # Bishop-like
        for dr, dc in self.BISHOP_DIRS:
            rr, cc = r+dr, c+dc
            while self._in_bounds(rr, cc):
                p = self.board[rr][cc]
                if p != 0:
                    if enemy_is_white and (p == self.WB or p == self.WQ): return True
                    if not enemy_is_white and (p == self.BB or p == self.BQ): return True
                    break
                rr += dr; cc += dc

        return False

    def _pins_and_checks(self):
        """Return (in_check, pins, checks) from perspective of side to move."""
        pins = []
        checks = []
        in_check = False

        king_r, king_c = self._king_pos(self._my_color())
        enemy_white = (self._enemy_color() == WHITE)

        # Directions from king for sliders
        for dr, dc in self.QUEEN_DIRS:
            possible_pin = None
            rr, cc = king_r + dr, king_c + dc
            while self._in_bounds(rr, cc):
                p = self.board[rr][cc]
                if p != 0:
                    # same color piece could be pinned
                    if (self._is_white(p) == (self._my_color() == WHITE)):
                        if possible_pin is None:
                            possible_pin = (rr, cc, dr, dc)
                        else:
                            # 2nd own piece blocks line -> no pin, no check along this ray
                            break
                    else:
                        # enemy piece: if it attacks along this ray -> check or pin
                        is_rook_like = (dr == 0 or dc == 0)
                        is_bishop_like = (dr != 0 and dc != 0)
                        if enemy_white:
                            if (is_rook_like and p in (self.WR, self.WQ)) or \
                               (is_bishop_like and p in (self.WB, self.WQ)):
                                if possible_pin is None:
                                    in_check = True
                                    checks.append((rr, cc, dr, dc))
                                else:
                                    pins.append(possible_pin)
                                break
                        else:
                            if (is_rook_like and p in (self.BR, self.BQ)) or \
                               (is_bishop_like and p in (self.BB, self.BQ)):
                                if possible_pin is None:
                                    in_check = True
                                    checks.append((rr, cc, dr, dc))
                                else:
                                    pins.append(possible_pin)
                                break
                        # enemy but not slider in this dir
                        break
                rr += dr; cc += dc

        # Knight checks
        for dr, dc in self.KNIGHT_DIRS:
            rr, cc = king_r + dr, king_c + dc
            if self._in_bounds(rr, cc):
                p = self.board[rr][cc]
                if enemy_white and p == self.WN: 
                    in_check = True; checks.append((rr, cc, dr, dc))
                if not enemy_white and p == self.BN: 
                    in_check = True; checks.append((rr, cc, dr, dc))

        # Pawn checks
        pawn_dirs = [(-1,-1), (-1,1)] if enemy_white else [(1,-1), (1,1)]
        for dr, dc in pawn_dirs:
            rr, cc = king_r + dr, king_c + dc
            if self._in_bounds(rr, cc):
                p = self.board[rr][cc]
                if enemy_white and p == self.WP:
                    in_check = True; checks.append((rr, cc, dr, dc))
                if not enemy_white and p == self.BP:
                    in_check = True; checks.append((rr, cc, dr, dc))

        # King adjacency (rarely relevant but safe)
        for dr, dc in self.KING_DIRS:
            rr, cc = king_r + dr, king_c + dc
            if self._in_bounds(rr, cc):
                p = self.board[rr][cc]
                if enemy_white and p == self.WK:
                    in_check = True; checks.append((rr, cc, dr, dc))
                if not enemy_white and p == self.BK:
                    in_check = True; checks.append((rr, cc, dr, dc))

        return in_check, pins, checks

    # -------------------- Public move gen --------------------
    def getValidMoves(self):
        moves = []
        in_check, pins, checks = self._pins_and_checks()

        # Pin map for quick lookup: (r,c) -> (dr,dc) pin direction
        pin_dir = {(r,c):(dr,dc) for (r,c,dr,dc) in pins}

        if in_check:
            if len(checks) == 1:
                # Evasions: move king, capture checker, block ray
                self._king_moves(*self._king_pos(self._my_color()), moves, only_legal=True)
                # Non-king moves can either capture the checking piece or block the ray
                check_r, check_c, dr, dc = checks[0]
                squares_to_block = []
                kr, kc = self._king_pos(self._my_color())
                rr, cc = kr + dr, kc + dc
                while (rr, cc) != (check_r, check_c):
                    squares_to_block.append((rr, cc))
                    rr += dr; cc += dc
                targets = {(check_r, check_c)} | set(squares_to_block)
                self._all_piece_moves(moves, pin_dir, target_filter=targets)
            else:
                # Double check: only king moves
                self._king_moves(*self._king_pos(self._my_color()), moves, only_legal=True)
        else:
            # Normal: all legal moves + castling
            self._all_piece_moves(moves, pin_dir)
            self._castle_moves(moves)

        return moves

    def _all_piece_moves(self, moves, pin_dir, target_filter=None):
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p == 0: continue
                if (self._is_white(p) and self.whiteToMove) or (self._is_black(p) and not self.whiteToMove):
                    # If pinned, restrict direction inside generators
                    if p in (self.WP, self.BP):
                        self._pawn_moves(r, c, moves, pin_dir.get((r,c)), target_filter)
                    elif p in (self.WN, self.BN):
                        self._knight_moves(r, c, moves, pin_dir.get((r,c)), target_filter)
                    elif p in (self.WB, self.BB):
                        self._bishop_moves(r, c, moves, pin_dir.get((r,c)), target_filter)
                    elif p in (self.WR, self.BR):
                        self._rook_moves(r, c, moves, pin_dir.get((r,c)), target_filter)
                    elif p in (self.WQ, self.BQ):
                        self._queen_moves(r, c, moves, pin_dir.get((r,c)), target_filter)
                    else:
                        self._king_moves(r, c, moves, only_legal=True)  # king never “pins”-restricted

    # -------------------- Piece move generators --------------------
    def _dir_allowed_by_pin(self, dr, dc, pinvec):
        if pinvec is None: return True
        # Move must be along the pin direction or directly opposite
        return (dr, dc) == pinvec or (dr, dc) == (-pinvec[0], -pinvec[1])

    def _pawn_moves(self, r, c, moves, pinvec=None, target_filter=None):
        piece = self.board[r][c]
        white = self._is_white(piece)
        step = -1 if white else 1
        start_row = 6 if white else 1
        promo_row = 0 if white else 7
        enemy = self._is_black if white else self._is_white

        # Forward 1
        nr, nc = r + step, c
        if self._in_bounds(nr, nc) and self.board[nr][nc] == 0:
            if pinvec is None or self._dir_allowed_by_pin(step, 0, pinvec):
                self._push_pawn_move(r, c, nr, nc, moves, promo_row, target_filter)

                # Forward 2 from start
                nr2 = r + 2*step
                if r == start_row and self.board[nr2][nc] == 0:
                    if target_filter is None or (nr2, nc) in target_filter:
                        moves.append(Move((r, c), (nr2, nc), self.board))

        # Captures
        for dc in (-1, +1):
            nr, nc = r + step, c + dc
            if not self._in_bounds(nr, nc): continue
            if pinvec is not None and not self._dir_allowed_by_pin(step, dc, pinvec): 
                continue
            if enemy(self.board[nr][nc]) or (self.enPassant == (nr, nc)):
                # En passant
                is_ep = (self.enPassant == (nr, nc)) and self.board[nr][nc] == 0
                if is_ep:
                    # Legality: the move must not leave king in check (handle by make/undo test)
                    m = Move((r, c), (nr, nc), self.board, is_en_passant=True)
                    if target_filter is None or (nr, nc) in target_filter:
                        if self._legal_if_made(m):
                            moves.append(m)
                else:
                    self._push_pawn_move(r, c, nr, nc, moves, promo_row, target_filter)

    def _push_pawn_move(self, r, c, nr, nc, moves, promo_row, target_filter):
        is_promo = (nr == promo_row)
        if target_filter is not None and (nr, nc) not in target_filter:
            return
        moves.append(Move((r, c), (nr, nc), self.board, is_promotion=is_promo))

    def _knight_moves(self, r, c, moves, pinvec=None, target_filter=None):
        # Knights cannot move if pinned (unless exactly on pin line, which for knights is impossible)
        if pinvec is not None: 
            return
        my_white = self.whiteToMove
        for dr, dc in self.KNIGHT_DIRS:
            nr, nc = r+dr, c+dc
            if not self._in_bounds(nr, nc): continue
            tgt = self.board[nr][nc]
            if tgt == 0 or (self._is_white(tgt) != my_white):
                if target_filter is None or (nr, nc) in target_filter:
                    m = Move((r, c), (nr, nc), self.board)
                    if self._legal_if_made(m):
                        moves.append(m)

    def _sliding(self, r, c, moves, dirs, pinvec, target_filter):
        my_white = self.whiteToMove
        for dr, dc in dirs:
            if pinvec is not None and not self._dir_allowed_by_pin(dr, dc, pinvec):
                continue
            nr, nc = r+dr, c+dc
            while self._in_bounds(nr, nc):
                tgt = self.board[nr][nc]
                if tgt == 0:
                    if target_filter is None or (nr, nc) in target_filter:
                        m = Move((r, c), (nr, nc), self.board)
                        if self._legal_if_made(m):
                            moves.append(m)
                else:
                    if self._is_white(tgt) != my_white:
                        if target_filter is None or (nr, nc) in target_filter:
                            m = Move((r, c), (nr, nc), self.board)
                            if self._legal_if_made(m):
                                moves.append(m)
                    break
                nr += dr; nc += dc

    def _bishop_moves(self, r, c, moves, pinvec=None, target_filter=None):
        self._sliding(r, c, moves, self.BISHOP_DIRS, pinvec, target_filter)

    def _rook_moves(self, r, c, moves, pinvec=None, target_filter=None):
        self._sliding(r, c, moves, self.ROOK_DIRS, pinvec, target_filter)

    def _queen_moves(self, r, c, moves, pinvec=None, target_filter=None):
        self._sliding(r, c, moves, self.QUEEN_DIRS, pinvec, target_filter)

    def _king_moves(self, r, c, moves, only_legal=False):
        my_white = self.whiteToMove
        for dr, dc in self.KING_DIRS:
            nr, nc = r+dr, c+dc
            if not self._in_bounds(nr, nc): continue
            tgt = self.board[nr][nc]
            if tgt == 0 or (self._is_white(tgt) != my_white):
                # King cannot move into check
                if not self.is_square_attacked(nr, nc, self._enemy_color()):
                    m = Move((r, c), (nr, nc), self.board)
                    moves.append(m)

    # -------------------- Castling --------------------
    def _castle_moves(self, moves):
        kr, kc = self._king_pos(self._my_color())
        if self._my_color() == WHITE:
            wk, wq = self.castlingRights[0], self.castlingRights[1]
            if wk and self.board[7][5] == 0 and self.board[7][6] == 0:
                if not self.is_square_attacked(7,4,BLACK) and not self.is_square_attacked(7,5,BLACK) and not self.is_square_attacked(7,6,BLACK):
                    moves.append(Move((7,4),(7,6), self.board, is_castle=True))
            if wq and self.board[7][1] == 0 and self.board[7][2] == 0 and self.board[7][3] == 0:
                if not self.is_square_attacked(7,4,BLACK) and not self.is_square_attacked(7,3,BLACK) and not self.is_square_attacked(7,2,BLACK):
                    moves.append(Move((7,4),(7,2), self.board, is_castle=True))
        else:
            bk, bq = self.castlingRights[2], self.castlingRights[3]
            if bk and self.board[0][5] == 0 and self.board[0][6] == 0:
                if not self.is_square_attacked(0,4,WHITE) and not self.is_square_attacked(0,5,WHITE) and not self.is_square_attacked(0,6,WHITE):
                    moves.append(Move((0,4),(0,6), self.board, is_castle=True))
            if bq and self.board[0][1] == 0 and self.board[0][2] == 0 and self.board[0][3] == 0:
                if not self.is_square_attacked(0,4,WHITE) and not self.is_square_attacked(0,3,WHITE) and not self.is_square_attacked(0,2,WHITE):
                    moves.append(Move((0,4),(0,2), self.board, is_castle=True))

    # -------------------- Legality check on a single candidate --------------------
    def _legal_if_made(self, move):
        """Make-move / undo-move on the *single* candidate only when necessary."""
        self.makeMove(move)
        king_r, king_c = self._king_pos(self._enemy_color())  # after move, side to move flipped
        in_check = self.is_square_attacked(king_r, king_c, self._my_color())  # enemy color is now to-move
        self.undoMove()
        return not in_check


class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start, end, board, is_promotion=False, is_en_passant=False, is_castle=False):
        self.startRow, self.startCol = start
        self.endRow, self.endCol = end
        self.moved_piece = board[self.startRow][self.startCol]
        self.captured_piece = board[self.endRow][self.endCol]
        self.is_promotion = is_promotion
        self.is_en_passant = is_en_passant
        self.is_castle = is_castle

        # For undo
        self.prev_en_passant = None
        self.prev_castle_rights = None

        self.id = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol \
                  + (10000 if self.is_promotion else 0) \
                  + (20000 if self.is_en_passant else 0) \
                  + (30000 if self.is_castle else 0)

    def __eq__(self, other): 
        return isinstance(other, Move) and self.id == other.id

    def getRankFile(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
