import pygame
import os
import sys
import copy

# Initialize Pygame
pygame.init()

# Constants
BOARD_SIZE = 800          # Chessboard size (800x800)
SIDEBAR_WIDTH = 300       # Sidebar width for UI elements
WIDTH, HEIGHT = BOARD_SIZE + SIDEBAR_WIDTH, BOARD_SIZE  # Total window size
ROWS, COLS = 8, 8
SQUARE_SIZE = BOARD_SIZE // COLS
BORDER_WIDTH = 10         # Thickness of the chessboard border

# Colors
WHITE = (245, 245, 220)        # Light squares
BLACK = (139, 69, 19)          # Dark squares
BLUE = (0, 0, 255)             # Selected piece highlight
GREEN = (0, 255, 0)             # Valid moves highlight
GREY = (128, 128, 128)         # Border color
RED = (255, 0, 0)               # Win message color
LIGHT_GREY = (211, 211, 211)    # Sidebar background
BLACK_TEXT = (0, 0, 0)          # Black text
WHITE_TEXT = (255, 255, 255)    # White text
BUTTON_COLOR = (70, 130, 180)    # SteelBlue for buttons
BUTTON_HOVER_COLOR = (100, 149, 237)  # CornflowerBlue when hovered

# Set up the display
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Chess')

# Load images
pieces = {}
def load_images():
    """
    Load all chess piece images into the 'pieces' dictionary.
    Ensure that the 'assets' folder contains all required images.
    """
    pieces_types = ['wp', 'wr', 'wn', 'wb', 'wq', 'wk', 
                   'bp', 'br', 'bn', 'bb', 'bq', 'bk']
    for piece in pieces_types:
        path = os.path.join('assets', f'{piece}.png')
        if not os.path.exists(path):
            print(f"Error: Image file '{path}' does not exist.")
            pygame.quit()
            sys.exit()
        try:
            pieces[piece] = pygame.transform.scale(
                pygame.image.load(path),
                (SQUARE_SIZE, SQUARE_SIZE)
            )
            print(f"Loaded image for {piece}")
        except pygame.error as e:
            print(f"Error loading {piece}.png: {e}")
            pygame.quit()
            sys.exit()

class Piece:
    def __init__(self, name, row, col, color):
        """
        Initialize a chess piece.
        
        :param name: Single character representing the piece type ('p', 'r', 'n', 'b', 'q', 'k')
        :param row: Row position on the board (0-7)
        :param col: Column position on the board (0-7)
        :param color: 'w' for white or 'b' for black
        """
        self.name = name
        self.row = row
        self.col = col
        self.color = color
        key = self.color + self.name
        if key not in pieces:
            print(f"Error: Piece image '{key}' not found in 'pieces' dictionary.")
            pygame.quit()
            sys.exit()
        self.image = pieces[key]
        self.has_moved = False  # For castling and pawn initial move

    def __deepcopy__(self, memo):
        """
        Custom deepcopy method to avoid copying the pygame.Surface object.
        
        :param memo: Dictionary for memoization (handled by copy.deepcopy)
        :return: A new Piece instance with the same attributes, excluding the image.
        """
        new_piece = Piece(self.name, self.row, self.col, self.color)
        new_piece.has_moved = self.has_moved
        # Reassign the image from the already loaded images
        new_piece.image = pieces[self.color + self.name]
        return new_piece

    def draw(self, win):
        """
        Draw the piece on the game window.
        
        :param win: Pygame window surface
        """
        win.blit(self.image, (self.col * SQUARE_SIZE, self.row * SQUARE_SIZE))

    def get_valid_moves(self, board, en_passant_target=None):
        """
        Get all valid moves for this piece.
        
        :param board: Current state of the board
        :param en_passant_target: Tuple (row, col) if en passant is possible
        :return: List of tuples representing valid move positions [(row, col), ...]
        """
        if self.name == 'p':
            return self.get_pawn_moves(board, en_passant_target)
        elif self.name == 'r':
            return self.get_rook_moves(board)
        elif self.name == 'n':
            return self.get_knight_moves(board)
        elif self.name == 'b':
            return self.get_bishop_moves(board)
        elif self.name == 'q':
            return self.get_queen_moves(board)
        elif self.name == 'k':
            return self.get_king_moves(board)
        return []

    def get_pawn_moves(self, board, en_passant_target=None):
        """
        Get valid moves for a pawn.
        
        :param board: Current state of the board
        :param en_passant_target: Tuple (row, col) if en passant is possible
        :return: List of tuples representing valid move positions [(row, col), ...]
        """
        moves = []
        direction = -1 if self.color == 'w' else 1
        start_row = 6 if self.color == 'w' else 1

        # Move forward one square
        new_row = self.row + direction
        if 0 <= new_row < ROWS and board[new_row][self.col] == 0:
            moves.append((new_row, self.col))
            # Move forward two squares from starting position
            new_row_two = new_row + direction
            if self.row == start_row and 0 <= new_row_two < ROWS and board[new_row_two][self.col] == 0:
                moves.append((new_row_two, self.col))

        # Capture diagonally to the left
        new_col = self.col - 1
        if 0 <= new_col < COLS and 0 <= new_row < ROWS:
            target = board[new_row][new_col]
            if target != 0 and target.color != self.color:
                moves.append((new_row, new_col))
            # En passant
            if en_passant_target == (new_row, new_col):
                moves.append((new_row, new_col))

        # Capture diagonally to the right
        new_col = self.col + 1
        if 0 <= new_col < COLS and 0 <= new_row < ROWS:
            target = board[new_row][new_col]
            if target != 0 and target.color != self.color:
                moves.append((new_row, new_col))
            # En passant
            if en_passant_target == (new_row, new_col):
                moves.append((new_row, new_col))

        return moves

    def get_rook_moves(self, board):
        """
        Get valid moves for a rook.
        
        :param board: Current state of the board
        :return: List of tuples representing valid move positions [(row, col), ...]
        """
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

        for d in directions:
            row, col = self.row + d[0], self.col + d[1]
            while 0 <= row < ROWS and 0 <= col < COLS:
                if board[row][col] == 0:
                    moves.append((row, col))
                else:
                    if board[row][col].color != self.color:
                        moves.append((row, col))
                    break
                row += d[0]
                col += d[1]

        return moves

    def get_knight_moves(self, board):
        """
        Get valid moves for a knight.
        
        :param board: Current state of the board
        :return: List of tuples representing valid move positions [(row, col), ...]
        """
        moves = []
        move_offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for offset in move_offsets:
            row = self.row + offset[0]
            col = self.col + offset[1]
            if 0 <= row < ROWS and 0 <= col < COLS:
                target = board[row][col]
                if target == 0 or target.color != self.color:
                    moves.append((row, col))

        return moves

    def get_bishop_moves(self, board):
        """
        Get valid moves for a bishop.
        
        :param board: Current state of the board
        :return: List of tuples representing valid move positions [(row, col), ...]
        """
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Diagonals

        for d in directions:
            row, col = self.row + d[0], self.col + d[1]
            while 0 <= row < ROWS and 0 <= col < COLS:
                if board[row][col] == 0:
                    moves.append((row, col))
                else:
                    if board[row][col].color != self.color:
                        moves.append((row, col))
                    break
                row += d[0]
                col += d[1]

        return moves

    def get_queen_moves(self, board):
        """
        Get valid moves for a queen.
        
        :param board: Current state of the board
        :return: List of tuples representing valid move positions [(row, col), ...]
        """
        # Queen's moves are combination of rook and bishop
        return self.get_rook_moves(board) + self.get_bishop_moves(board)

    def get_king_moves(self, board):
        """
        Get valid moves for a king, including castling.
        
        :param board: Current state of the board
        :return: List of tuples representing valid move positions [(row, col), ...]
        """
        moves = []
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),          (0, 1),
            (1, -1),  (1, 0), (1, 1)
        ]

        for d in directions:
            row = self.row + d[0]
            col = self.col + d[1]
            if 0 <= row < ROWS and 0 <= col < COLS:
                target = board[row][col]
                if target == 0 or target.color != self.color:
                    # Temporarily move the king to the new square
                    original_row, original_col = self.row, self.col
                    self.row, self.col = row, col
                    in_check = is_in_check(board, self.color)
                    self.row, self.col = original_row, original_col
                    if not in_check:
                        moves.append((row, col))

        # Castling
        if not self.has_moved and not is_in_check(board, self.color):
            # Kingside Castling
            if can_castle_kingside(board, self.color):
                moves.append((self.row, self.col + 2))
            # Queenside Castling
            if can_castle_queenside(board, self.color):
                moves.append((self.row, self.col - 2))

        return moves

def can_castle_kingside(board, color):
    """
    Check if the player can perform kingside castling.
    
    :param board: Current state of the board
    :param color: 'w' or 'b'
    :return: Boolean indicating if kingside castling is possible
    """
    row = 7 if color == 'w' else 0
    king = board[row][4]
    rook = board[row][7]
    if rook == 0 or rook.name != 'r' or rook.color != color or rook.has_moved:
        return False
    # Check squares between king and rook
    for col in range(5, 7):
        if board[row][col] != 0:
            return False
    # Check if squares king passes through are under attack
    for col in range(4, 7):
        if is_square_under_attack(board, (row, col), color):
            return False
    return True

def can_castle_queenside(board, color):
    """
    Check if the player can perform queenside castling.
    
    :param board: Current state of the board
    :param color: 'w' or 'b'
    :return: Boolean indicating if queenside castling is possible
    """
    row = 7 if color == 'w' else 0
    king = board[row][4]
    rook = board[row][0]
    if rook == 0 or rook.name != 'r' or rook.color != color or rook.has_moved:
        return False
    # Check squares between king and rook
    for col in range(1, 4):
        if board[row][col] != 0:
            return False
    # Check if squares king passes through are under attack
    for col in range(2, 5):
        if is_square_under_attack(board, (row, col), color):
            return False
    return True

def is_square_under_attack(board, square, color):
    """
    Determine if a square is under attack by the opponent.
    
    :param board: Current state of the board
    :param square: Tuple (row, col) representing the square to check
    :param color: 'w' or 'b' representing the current player's color
    :return: Boolean indicating if the square is under attack
    """
    opponent_color = 'b' if color == 'w' else 'w'
    for row in board:
        for piece in row:
            if piece != 0 and piece.color == opponent_color:
                # **Important Fix:** Skip opponent's king to prevent recursion
                if piece.name == 'k':
                    continue
                moves = piece.get_valid_moves(board)
                if square in moves:
                    return True
    return False

def draw_board(win):
    """
    Draw the chessboard on the window, including the border.
    
    :param win: Pygame window surface
    """
    colors = [WHITE, BLACK]
    for row in range(ROWS):
        for col in range(COLS):
            color = colors[(row + col) % 2]
            pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    # Draw border around the chessboard
    border_color = GREY
    pygame.draw.rect(win, border_color, (0, 0, BOARD_SIZE, BOARD_SIZE), BORDER_WIDTH)

def create_board():
    """
    Create the initial chessboard setup with all pieces in their starting positions.
    
    :return: 2D list representing the board with Piece instances or 0 for empty squares
    """
    board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    
    # Place Black Pieces
    board[0][0] = Piece('r', 0, 0, 'b')
    board[0][1] = Piece('n', 0, 1, 'b')
    board[0][2] = Piece('b', 0, 2, 'b')
    board[0][3] = Piece('q', 0, 3, 'b')
    board[0][4] = Piece('k', 0, 4, 'b')
    board[0][5] = Piece('b', 0, 5, 'b')
    board[0][6] = Piece('n', 0, 6, 'b')
    board[0][7] = Piece('r', 0, 7, 'b')
    for col in range(COLS):
        board[1][col] = Piece('p', 1, col, 'b')
    
    # Place White Pieces
    board[7][0] = Piece('r', 7, 0, 'w')
    board[7][1] = Piece('n', 7, 1, 'w')
    board[7][2] = Piece('b', 7, 2, 'w')
    board[7][3] = Piece('q', 7, 3, 'w')
    board[7][4] = Piece('k', 7, 4, 'w')
    board[7][5] = Piece('b', 7, 5, 'w')
    board[7][6] = Piece('n', 7, 6, 'w')
    board[7][7] = Piece('r', 7, 7, 'w')
    for col in range(COLS):
        board[6][col] = Piece('p', 6, col, 'w')
    
    return board

# Initialize Fonts
FONT = pygame.font.SysFont('Arial', 24)
WIN_FONT = pygame.font.SysFont('Arial', 36, bold=True)
BUTTON_FONT = pygame.font.SysFont('Arial', 28, bold=True)

def draw_sidebar(win, turn, move_history, captured_white, captured_black, game_over=False, winner=None):
    """
    Draw the sidebar containing the turn indicator, move history, captured pieces, and Undo button.
    
    :param win: Pygame window surface
    :param turn: 'w' for White's turn or 'b' for Black's turn
    :param move_history: List of move strings
    :param captured_white: List of captured white pieces
    :param captured_black: List of captured black pieces
    :param game_over: Boolean indicating if the game has ended
    :param winner: 'w' or 'b' indicating the winner
    :return: pygame.Rect object representing the Undo button
    """
    # Draw sidebar background
    sidebar_color = LIGHT_GREY
    pygame.draw.rect(win, sidebar_color, (BOARD_SIZE, 0, SIDEBAR_WIDTH, BOARD_SIZE))
    
    padding = 20
    current_y = padding
    
    # Display turn indicator
    if not game_over:
        turn_text = FONT.render(f"Turn: {'White' if turn == 'w' else 'Black'}", True, BLACK_TEXT)
        win.blit(turn_text, (BOARD_SIZE + 20, current_y))
        current_y += 30
    else:
        # Display win message
        if winner:
            win_message = f"{'White' if winner == 'w' else 'Black'} Wins!"
            win_text = WIN_FONT.render(win_message, True, RED)
            text_rect = win_text.get_rect(center=(BOARD_SIZE + SIDEBAR_WIDTH//2, 50))
            win.blit(win_text, text_rect)
            current_y += 80
        else:
            # Draw if no winner (e.g., draw)
            draw_text = FONT.render("Game Over", True, RED)
            text_rect = draw_text.get_rect(center=(BOARD_SIZE + SIDEBAR_WIDTH//2, 50))
            win.blit(draw_text, text_rect)
            current_y += 50
    
    # Display Move History
    history_title = FONT.render("Move History:", True, BLACK_TEXT)
    win.blit(history_title, (BOARD_SIZE + 20, current_y))
    current_y += 30
    for i, move in enumerate(move_history[-15:]):  # Show last 15 moves
        move_text = FONT.render(move, True, BLACK_TEXT)
        win.blit(move_text, (BOARD_SIZE + 20, current_y))
        current_y += 25
    
    current_y += 10  # Add space before captured pieces
    
    # Display Captured Pieces
    captured_title = FONT.render("Captured Pieces:", True, BLACK_TEXT)
    win.blit(captured_title, (BOARD_SIZE + 20, current_y))
    current_y += 30
    
    # Captured White Pieces
    white_captured_text = FONT.render("White:", True, BLACK_TEXT)
    win.blit(white_captured_text, (BOARD_SIZE + 20, current_y))
    current_y += 25
    for piece in captured_white:
        piece_image = pieces.get(piece, None)
        if piece_image:
            win.blit(piece_image, (BOARD_SIZE + 20, current_y))
            current_y += 30
    
    current_y += 10  # Add space between white and black
    
    # Captured Black Pieces
    black_captured_text = FONT.render("Black:", True, BLACK_TEXT)
    win.blit(black_captured_text, (BOARD_SIZE + 20, current_y))
    current_y += 25
    for piece in captured_black:
        piece_image = pieces.get(piece, None)
        if piece_image:
            win.blit(piece_image, (BOARD_SIZE + 20, current_y))
            current_y += 30
    
    # Draw Undo Button
    button_width, button_height = 200, 50
    button_x = BOARD_SIZE + (SIDEBAR_WIDTH - button_width) // 2
    button_y = HEIGHT - button_height - padding
    undo_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    # Change button color on hover
    mouse_pos = pygame.mouse.get_pos()
    if undo_button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(win, BUTTON_HOVER_COLOR, undo_button_rect)
    else:
        pygame.draw.rect(win, BUTTON_COLOR, undo_button_rect)
    
    # Draw button text
    undo_text = BUTTON_FONT.render("Undo", True, WHITE_TEXT)
    text_rect = undo_text.get_rect(center=undo_button_rect.center)
    win.blit(undo_text, text_rect)
    
    return undo_button_rect  # Return the button's rectangle for click detection

def get_square_under_mouse(board):
    """
    Get the piece and its position under the current mouse position.
    
    :param board: Current state of the board
    :return: Tuple (piece, row, col) or (None, None, None) if out of bounds or on the border
    """
    mouse_pos = pygame.mouse.get_pos()
    x, y = mouse_pos

    # Check if click is outside the board area
    if x >= BOARD_SIZE or y >= BOARD_SIZE:
        return None, None, None  # Clicked outside the board and sidebar

    # Exclude border area
    if (x < BORDER_WIDTH or y < BORDER_WIDTH or
        x >= BOARD_SIZE - BORDER_WIDTH or y >= BOARD_SIZE - BORDER_WIDTH):
        return None, None, None  # Clicked on the border

    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE

    # Ensure row and col are within valid range
    if 0 <= row < ROWS and 0 <= col < COLS:
        return board[row][col], row, col

    return None, None, None

def check_win_condition(board):
    """
    Check if a king has been captured, indicating a win.
    
    :param board: Current state of the board
    :return: Tuple (game_over, winner) where:
             - game_over is True if the game has ended
             - winner is 'w' or 'b' indicating the winner, or None for no winner
    """
    white_king = False
    black_king = False
    for row in board:
        for piece in row:
            if piece != 0:
                if piece.name == 'k':
                    if piece.color == 'w':
                        white_king = True
                    elif piece.color == 'b':
                        black_king = True
    if not white_king:
        return True, 'b'  # Black wins
    if not black_king:
        return True, 'w'  # White wins
    return False, None  # No winner yet

def is_in_check(board, color):
    """
    Determine if the king of the specified color is in check.
    
    :param board: Current state of the board
    :param color: 'w' or 'b'
    :return: Boolean indicating if the king is in check
    """
    # Find the king's position
    king_pos = None
    for row in board:
        for piece in row:
            if piece != 0 and piece.name == 'k' and piece.color == color:
                king_pos = (piece.row, piece.col)
                break
    if not king_pos:
        return False  # King not found, already handled in win condition

    # Check all opponent pieces to see if they can attack the king
    opponent_color = 'b' if color == 'w' else 'w'
    for row in board:
        for piece in row:
            if piece != 0 and piece.color == opponent_color:
                # **Important Fix:** Skip opponent's king to prevent recursion
                if piece.name == 'k':
                    continue
                moves = piece.get_valid_moves(board)
                if king_pos in moves:
                    return True
    return False

def is_checkmate(board, color):
    """
    Determine if the player of the specified color is in checkmate.
    
    :param board: Current state of the board
    :param color: 'w' or 'b'
    :return: Boolean indicating if the player is in checkmate
    """
    if not is_in_check(board, color):
        return False
    # Get all valid moves for the player
    for row in board:
        for piece in row:
            if piece != 0 and piece.color == color:
                moves = piece.get_valid_moves(board)
                for move in moves:
                    # Make a temporary copy of the board and make the move
                    temp_board = copy.deepcopy(board)
                    temp_piece = temp_board[piece.row][piece.col]
                    temp_board[piece.row][piece.col] = 0
                    captured_piece = temp_board[move[0]][move[1]]
                    temp_board[move[0]][move[1]] = temp_piece
                    temp_piece.row, temp_piece.col = move[0], move[1]
                    # Handle castling moves separately
                    if piece.name == 'k' and abs(move[1] - 4) == 2:
                        if move[1] - 4 == 2:
                            # Kingside Castling
                            rook = temp_board[move[0]][7]
                            temp_board[move[0]][7] = 0
                            temp_board[move[0]][5] = rook
                            rook.row, rook.col = move[0], 5
                        elif move[1] - 4 == -2:
                            # Queenside Castling
                            rook = temp_board[move[0]][0]
                            temp_board[move[0]][0] = 0
                            temp_board[move[0]][3] = rook
                            rook.row, rook.col = move[0], 3
                    # Check if the king is still in check after the move
                    if not is_in_check(temp_board, color):
                        return False
    return True

def promote_pawn(screen, piece):
    """
    Handle pawn promotion by allowing the player to choose a piece to promote to.
    
    :param screen: Pygame window surface
    :param piece: The pawn piece to be promoted
    :return: The new promoted Piece instance
    """
    promotion = False
    choice = 'q'  # Default promotion to Queen

    while not promotion:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    choice = 'q'
                    promotion = True
                elif event.key == pygame.K_r:
                    choice = 'r'
                    promotion = True
                elif event.key == pygame.K_b:
                    choice = 'b'
                    promotion = True
                elif event.key == pygame.K_n:
                    choice = 'n'
                    promotion = True

        # Display promotion options
        font = pygame.font.SysFont('Arial', 30)
        text = font.render("Promote to (Q/R/B/N): ", True, BLACK_TEXT)
        # Clear the promotion area
        pygame.draw.rect(screen, LIGHT_GREY, (BOARD_SIZE + 10, HEIGHT//2 - 30, SIDEBAR_WIDTH - 20, 60))
        screen.blit(text, (BOARD_SIZE + 20, HEIGHT//2 - 30))
        pygame.display.flip()
    
    return Piece(choice, piece.row, piece.col, piece.color)

def move_puts_king_in_check(board, piece, move, color):
    """
    Determine if making a move would put the player's king in check.
    
    :param board: Current state of the board
    :param piece: Piece being moved
    :param move: Tuple (row, col) indicating the move
    :param color: 'w' or 'b'
    :return: True if the move puts the king in check, False otherwise
    """
    temp_board = copy.deepcopy(board)
    temp_piece = temp_board[piece.row][piece.col]
    temp_board[piece.row][piece.col] = 0
    captured_piece = temp_board[move[0]][move[1]]
    temp_board[move[0]][move[1]] = temp_piece
    temp_piece.row, temp_piece.col = move[0], move[1]
    return is_in_check(temp_board, color)

def draw_sidebar(win, turn, move_history, captured_white, captured_black, game_over=False, winner=None):
    """
    Draw the sidebar containing the turn indicator, move history, captured pieces, and Undo button.
    
    :param win: Pygame window surface
    :param turn: 'w' for White's turn or 'b' for Black's turn
    :param move_history: List of move strings
    :param captured_white: List of captured white pieces
    :param captured_black: List of captured black pieces
    :param game_over: Boolean indicating if the game has ended
    :param winner: 'w' or 'b' indicating the winner
    :return: pygame.Rect object representing the Undo button
    """
    # Draw sidebar background
    sidebar_color = LIGHT_GREY
    pygame.draw.rect(win, sidebar_color, (BOARD_SIZE, 0, SIDEBAR_WIDTH, BOARD_SIZE))
    
    padding = 20
    current_y = padding
    
    # Display turn indicator
    if not game_over:
        turn_text = FONT.render(f"Turn: {'White' if turn == 'w' else 'Black'}", True, BLACK_TEXT)
        win.blit(turn_text, (BOARD_SIZE + 20, current_y))
        current_y += 30
    else:
        # Display win message
        if winner:
            win_message = f"{'White' if winner == 'w' else 'Black'} Wins!"
            win_text = WIN_FONT.render(win_message, True, RED)
            text_rect = win_text.get_rect(center=(BOARD_SIZE + SIDEBAR_WIDTH//2, 50))
            win.blit(win_text, text_rect)
            current_y += 80
        else:
            # Draw if no winner (e.g., draw)
            draw_text = FONT.render("Game Over", True, RED)
            text_rect = draw_text.get_rect(center=(BOARD_SIZE + SIDEBAR_WIDTH//2, 50))
            win.blit(draw_text, text_rect)
            current_y += 50
    
    # Display Move History
    history_title = FONT.render("Move History:", True, BLACK_TEXT)
    win.blit(history_title, (BOARD_SIZE + 20, current_y))
    current_y += 30
    for i, move in enumerate(move_history[-15:]):  # Show last 15 moves
        move_text = FONT.render(move, True, BLACK_TEXT)
        win.blit(move_text, (BOARD_SIZE + 20, current_y))
        current_y += 25
    
    current_y += 10  # Add space before captured pieces
    
    # Display Captured Pieces
    captured_title = FONT.render("Captured Pieces:", True, BLACK_TEXT)
    win.blit(captured_title, (BOARD_SIZE + 20, current_y))
    current_y += 30
    
    # Captured White Pieces
    white_captured_text = FONT.render("White:", True, BLACK_TEXT)
    win.blit(white_captured_text, (BOARD_SIZE + 20, current_y))
    current_y += 25
    for piece in captured_white:
        piece_image = pieces.get(piece, None)
        if piece_image:
            win.blit(piece_image, (BOARD_SIZE + 20, current_y))
            current_y += 30
    
    current_y += 10  # Add space between white and black
    
    # Captured Black Pieces
    black_captured_text = FONT.render("Black:", True, BLACK_TEXT)
    win.blit(black_captured_text, (BOARD_SIZE + 20, current_y))
    current_y += 25
    for piece in captured_black:
        piece_image = pieces.get(piece, None)
        if piece_image:
            win.blit(piece_image, (BOARD_SIZE + 20, current_y))
            current_y += 30
    
    # Draw Undo Button
    button_width, button_height = 200, 50
    button_x = BOARD_SIZE + (SIDEBAR_WIDTH - button_width) // 2
    button_y = HEIGHT - button_height - padding
    undo_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    # Change button color on hover
    mouse_pos = pygame.mouse.get_pos()
    if undo_button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(win, BUTTON_HOVER_COLOR, undo_button_rect)
    else:
        pygame.draw.rect(win, BUTTON_COLOR, undo_button_rect)
    
    # Draw button text
    undo_text = BUTTON_FONT.render("Undo", True, WHITE_TEXT)
    text_rect = undo_text.get_rect(center=undo_button_rect.center)
    win.blit(undo_text, text_rect)
    
    return undo_button_rect  # Return the button's rectangle for click detection

def is_checkmate(board, color):
    """
    Determine if the player of the specified color is in checkmate.
    
    :param board: Current state of the board
    :param color: 'w' or 'b'
    :return: Boolean indicating if the player is in checkmate
    """
    if not is_in_check(board, color):
        return False
    # Get all valid moves for the player
    for row in board:
        for piece in row:
            if piece != 0 and piece.color == color:
                moves = piece.get_valid_moves(board)
                for move in moves:
                    # Make a temporary copy of the board and make the move
                    temp_board = copy.deepcopy(board)
                    temp_piece = temp_board[piece.row][piece.col]
                    temp_board[piece.row][piece.col] = 0
                    captured_piece = temp_board[move[0]][move[1]]
                    temp_board[move[0]][move[1]] = temp_piece
                    temp_piece.row, temp_piece.col = move[0], move[1]
                    # Handle castling moves separately
                    if piece.name == 'k' and abs(move[1] - 4) == 2:
                        if move[1] - 4 == 2:
                            # Kingside Castling
                            rook = temp_board[move[0]][7]
                            temp_board[move[0]][7] = 0
                            temp_board[move[0]][5] = rook
                            rook.row, rook.col = move[0], 5
                        elif move[1] - 4 == -2:
                            # Queenside Castling
                            rook = temp_board[move[0]][0]
                            temp_board[move[0]][0] = 0
                            temp_board[move[0]][3] = rook
                            rook.row, rook.col = move[0], 3
                    # Check if the king is still in check after the move
                    if not is_in_check(temp_board, color):
                        return False
    return True

def promote_pawn(screen, piece):
    """
    Handle pawn promotion by allowing the player to choose a piece to promote to.
    
    :param screen: Pygame window surface
    :param piece: The pawn piece to be promoted
    :return: The new promoted Piece instance
    """
    promotion = False
    choice = 'q'  # Default promotion to Queen

    while not promotion:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    choice = 'q'
                    promotion = True
                elif event.key == pygame.K_r:
                    choice = 'r'
                    promotion = True
                elif event.key == pygame.K_b:
                    choice = 'b'
                    promotion = True
                elif event.key == pygame.K_n:
                    choice = 'n'
                    promotion = True

        # Display promotion options
        font = pygame.font.SysFont('Arial', 30)
        text = font.render("Promote to (Q/R/B/N): ", True, BLACK_TEXT)
        # Clear the promotion area
        pygame.draw.rect(screen, LIGHT_GREY, (BOARD_SIZE + 10, HEIGHT//2 - 30, SIDEBAR_WIDTH - 20, 60))
        screen.blit(text, (BOARD_SIZE + 20, HEIGHT//2 - 30))
        pygame.display.flip()
    
    return Piece(choice, piece.row, piece.col, piece.color)

def move_puts_king_in_check(board, piece, move, color):
    """
    Determine if making a move would put the player's king in check.
    
    :param board: Current state of the board
    :param piece: Piece being moved
    :param move: Tuple (row, col) indicating the move
    :param color: 'w' or 'b'
    :return: True if the move puts the king in check, False otherwise
    """
    temp_board = copy.deepcopy(board)
    temp_piece = temp_board[piece.row][piece.col]
    temp_board[piece.row][piece.col] = 0
    captured_piece = temp_board[move[0]][move[1]]
    temp_board[move[0]][move[1]] = temp_piece
    temp_piece.row, temp_piece.col = move[0], move[1]
    return is_in_check(temp_board, color)

def main():
    """
    Main function to run the chess game.
    """
    run = True
    clock = pygame.time.Clock()
    
    load_images()      # Load images before creating the board
    board = create_board()
    
    selected_piece = None
    valid_moves = []
    turn = 'w'  # 'w' for White's turn, 'b' for Black's turn
    game_over = False
    winner = None
    move_history = []
    captured_white = []
    captured_black = []
    move_stack = []  # For undo functionality
    en_passant_target = None  # Square where en passant is possible

    while run:
        clock.tick(60)  # Limit to 60 FPS
        draw_board(WIN)
        undo_button_rect = draw_sidebar(WIN, turn, move_history, captured_white, captured_black, game_over, winner)

        # Highlight selected piece and its valid moves
        if selected_piece and not game_over:
            # Highlight the selected square
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill((0, 0, 255, 100))  # Semi-transparent blue
            WIN.blit(s, (selected_piece.col * SQUARE_SIZE, selected_piece.row * SQUARE_SIZE))
            
            # Highlight valid move squares
            for move in valid_moves:
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                s.fill((0, 255, 0, 100))  # Semi-transparent green
                WIN.blit(s, (move[1] * SQUARE_SIZE, move[0] * SQUARE_SIZE))

        # Draw pieces
        for row in board:
            for piece in row:
                if piece != 0:
                    piece.draw(WIN)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mouse_pos = pygame.mouse.get_pos()
                piece, row, col = get_square_under_mouse(board)
                
                # Check if click is on the Undo button
                if undo_button_rect and undo_button_rect.collidepoint(mouse_pos):
                    # Undo action
                    if move_stack:
                        previous_state = move_stack.pop()
                        board, turn, en_passant_target, move_history, captured_white, captured_black = copy.deepcopy(previous_state)
                        selected_piece = None
                        valid_moves = []
                        game_over = False
                        winner = None
                    continue  # Skip further processing for this click

                if selected_piece:
                    # Attempt to move the selected piece
                    if (row, col) in valid_moves:
                        # Save current state for undo
                        move_stack.append(copy.deepcopy((board, turn, en_passant_target, move_history.copy(), captured_white.copy(), captured_black.copy())))
                        
                        # Handle en passant capture
                        if selected_piece.name == 'p' and (row, col) == en_passant_target:
                            capture_row = selected_piece.row
                            capture_col = col
                            captured_piece = board[capture_row][capture_col]
                            board[capture_row][capture_col] = 0
                            if captured_piece.color == 'w':
                                captured_white.append(captured_piece.name + 'p')
                            else:
                                captured_black.append(captured_piece.name + 'p')
                        
                        # Move the piece
                        board[selected_piece.row][selected_piece.col] = 0
                        captured_piece = board[row][col]
                        if captured_piece != 0:
                            if captured_piece.color == 'w':
                                captured_white.append(captured_piece.name + 'p')
                            else:
                                captured_black.append(captured_piece.name + 'p')
                        board[row][col] = selected_piece
                        selected_piece.row, selected_piece.col = row, col
                        selected_piece.has_moved = True

                        # Handle castling
                        if selected_piece.name == 'k' and abs(col - 4) == 2:
                            # Kingside Castling
                            if col - 4 == 2:
                                rook = board[row][7]
                                board[row][7] = 0
                                board[row][5] = rook
                                rook.row = row
                                rook.col = 5
                                rook.has_moved = True
                            # Queenside Castling
                            elif col - 4 == -2:
                                rook = board[row][0]
                                board[row][0] = 0
                                board[row][3] = rook
                                rook.row = row
                                rook.col = 3
                                rook.has_moved = True

                        # Handle pawn promotion
                        if selected_piece.name == 'p' and (row == 0 or row == ROWS -1):
                            selected_piece = promote_pawn(WIN, selected_piece)
                            board[row][col] = selected_piece
                        
                        # Update en passant target
                        if selected_piece.name == 'p' and abs(row - (selected_piece.row - (-1 if selected_piece.color == 'w' else 1))) == 2:
                            en_passant_target = ((row + (selected_piece.row - (-1 if selected_piece.color == 'w' else 1))) //2, col)
                        else:
                            en_passant_target = None

                        # Update move history
                        move_number = len(move_history) //2 +1
                        move_san = f"{move_number}. {'White' if turn == 'w' else 'Black'}: {selected_piece.name.upper()} from ({selected_piece.row}, {selected_piece.col}) to ({row}, {col})"
                        move_history.append(move_san)
                        
                        # Check for win condition
                        game_over, winner = check_win_condition(board)
                        if not game_over:
                            # Check if the opponent is in check
                            opponent_color = 'b' if turn == 'w' else 'w'
                            if is_in_check(board, opponent_color):
                                in_check_text = f"{'White' if opponent_color == 'w' else 'Black'} is in Check!"
                                move_history.append(in_check_text)
                            
                            # Check for checkmate
                            if is_checkmate(board, opponent_color):
                                game_over = True
                                winner = 'w' if opponent_color == 'b' else 'b'
                                win_message = f"{'White' if winner == 'w' else 'Black'} wins by Checkmate!"
                                move_history.append(win_message)
                            
                            # Switch turns
                            turn = 'b' if turn == 'w' else 'w'
                        else:
                            # Append win message to move history
                            win_message = f"{'White' if winner == 'w' else 'Black'} wins by capturing the king!"
                            move_history.append(win_message)
                        
                        selected_piece = None
                        valid_moves = []
                    else:
                        # Select a different piece if it's the current player's
                        if piece != 0 and piece.color == turn:
                            selected_piece = piece
                            # Recalculate valid moves ensuring king isn't in check after move
                            valid_moves = [move for move in piece.get_valid_moves(board, en_passant_target) if not move_puts_king_in_check(board, piece, move, turn)]
                        else:
                            selected_piece = None
                            valid_moves = []
                else:
                    if piece != 0 and piece.color == turn:
                        # Check if player is in check and must move the king or block the check
                        if is_in_check(board, turn):
                            # Only allow moves that get out of check
                            valid_moves = [move for move in piece.get_valid_moves(board, en_passant_target) if not move_puts_king_in_check(board, piece, move, turn)]
                        else:
                            valid_moves = piece.get_valid_moves(board, en_passant_target)
                        selected_piece = piece

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    # Undo move
                    if move_stack:
                        previous_state = move_stack.pop()
                        board, turn, en_passant_target, move_history, captured_white, captured_black = copy.deepcopy(previous_state)
                        selected_piece = None
                        valid_moves = []
                        game_over = False
                        winner = None

                elif event.key == pygame.K_r:
                    # Restart game
                    board = create_board()
                    move_history = []
                    captured_white = []
                    captured_black = []
                    move_stack = []
                    selected_piece = None
                    valid_moves = []
                    turn = 'w'
                    game_over = False
                    winner = None
                    en_passant_target = None

def is_checkmate(board, color):
    """
    Determine if the player of the specified color is in checkmate.
    
    :param board: Current state of the board
    :param color: 'w' or 'b'
    :return: Boolean indicating if the player is in checkmate
    """
    if not is_in_check(board, color):
        return False
    # Get all valid moves for the player
    for row in board:
        for piece in row:
            if piece != 0 and piece.color == color:
                moves = piece.get_valid_moves(board)
                for move in moves:
                    # Make a temporary copy of the board and make the move
                    temp_board = copy.deepcopy(board)
                    temp_piece = temp_board[piece.row][piece.col]
                    temp_board[piece.row][piece.col] = 0
                    captured_piece = temp_board[move[0]][move[1]]
                    temp_board[move[0]][move[1]] = temp_piece
                    temp_piece.row, temp_piece.col = move[0], move[1]
                    # Handle castling moves separately
                    if piece.name == 'k' and abs(move[1] - 4) == 2:
                        if move[1] - 4 == 2:
                            # Kingside Castling
                            rook = temp_board[move[0]][7]
                            temp_board[move[0]][7] = 0
                            temp_board[move[0]][5] = rook
                            rook.row, rook.col = move[0], 5
                        elif move[1] - 4 == -2:
                            # Queenside Castling
                            rook = temp_board[move[0]][0]
                            temp_board[move[0]][0] = 0
                            temp_board[move[0]][3] = rook
                            rook.row, rook.col = move[0], 3
                    # Check if the king is still in check after the move
                    if not is_in_check(temp_board, color):
                        return False
    return True

if __name__ == '__main__':
    main()
