import pygame
import chess
import sys
import math
from time import time

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess AI")

# Piece values for evaluation
PIECE_VALUES = {
    chess.PAWN: 10,
    chess.KNIGHT: 30,
    chess.BISHOP: 30,
    chess.ROOK: 50,
    chess.QUEEN: 90,
    chess.KING: 900
}

# Colors and font
WHITE = (245, 245, 220)  # Softer white for board
DARK_GRAY = (100, 100, 100)  # Slightly lighter gray
HIGHLIGHT = (255, 215, 0, 100)  # Semi-transparent yellow for highlights
SQUARE_SIZE = WIDTH // 8
font = pygame.font.SysFont('Segoe UI Symbol', 64)
info_font = pygame.font.SysFont('Arial', 20)

# Piece symbols
PIECE_SYMBOLS = {
    'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♕', 'K': '♚', 'P': '♙',
    'r': '♖', 'n': '♘', 'b': '♗', 'q': '♛', 'k': '♔', 'p': '♟'
}

def draw_board(screen, board, selected=None, last_move=None):
    # Pre-render board colors
    for row in range(8):
        for col in range(8):
            is_light = (row + col) % 2 == 0
            square_color = WHITE if is_light else DARK_GRAY
            pygame.draw.rect(screen, square_color, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Highlight last move
    if last_move:
        for square in (last_move.from_square, last_move.to_square):
            col, row = square % 8, 7 - (square // 8)
            pygame.draw.rect(screen, HIGHLIGHT, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Draw pieces
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            col, row = square % 8, 7 - (square // 8)
            is_light = (row + col) % 2 == 0
            text_color = (50, 50, 50) if is_light else (200, 200, 200)
            symbol = PIECE_SYMBOLS[piece.symbol()]
            text = font.render(symbol, True, text_color)
            text_rect = text.get_rect(center=(col*SQUARE_SIZE + SQUARE_SIZE//2, row*SQUARE_SIZE + SQUARE_SIZE//2))
            screen.blit(text, text_rect)

    # Highlight selected square
    if selected:
        col, row = selected % 8, 7 - (selected // 8)
        pygame.draw.rect(screen, (255, 0, 0), (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

def evaluate_board(board):
    if board.is_checkmate():
        return 10000 if board.turn else -10000
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    evaluation = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            evaluation += value * (-1 if piece.color else 1)
    return evaluation

def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    
    if maximizing_player:
        max_eval = -math.inf
        for move in board.legal_moves:
            board.push(move)
            evaluation = minimax(board, depth-1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in board.legal_moves:
            board.push(move)
            evaluation = minimax(board, depth-1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, evaluation)
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return min_eval

def get_ai_move(board, depth=3):
    start_time = time()
    best_move = None
    best_value = -math.inf
    for move in board.legal_moves:
        board.push(move)
        value = minimax(board, depth-1, -math.inf, math.inf, False)
        board.pop()
        if value > best_value:
            best_value = value
            best_move = move
    print(f"AI move took {time() - start_time:.2f} seconds")
    return best_move

def draw_info(screen, board, last_move_time):
    # Display game status and last move time
    status = "White's turn" if board.turn else "Black's turn"
    status_text = info_font.render(status, True, (0, 0, 0))
    time_text = info_font.render(f"Last move: {last_move_time:.2f}s", True, (0, 0, 0))
    screen.blit(status_text, (10, HEIGHT - 40))
    screen.blit(time_text, (10, HEIGHT - 20))

def main():
    board = chess.Board()
    selected = None
    player_color = chess.WHITE
    last_move = None
    last_move_time = 0.0
    clock = pygame.time.Clock()

    while not board.is_game_over():
        clock.tick(60)  # Limit to 60 FPS
        if board.turn == player_color:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    col = x // SQUARE_SIZE
                    row = y // SQUARE_SIZE
                    square = chess.square(col, 7-row)
                    piece = board.piece_at(square)
                    
                    if selected:
                        move = chess.Move(selected, square)
                        if move in board.legal_moves:
                            start_time = time()
                            board.push(move)
                            last_move_time = time() - start_time
                            last_move = move
                            selected = None
                        elif piece and piece.color == player_color:
                            selected = square
                        else:
                            selected = None
                    elif piece and piece.color == player_color:
                        selected = square
        else:
            start_time = time()
            ai_move = get_ai_move(board, depth=3)
            board.push(ai_move)
            last_move_time = time() - start_time
            last_move = ai_move
        
        screen.fill((200, 200, 200))  # Light gray background
        draw_board(screen, board, selected, last_move)
        draw_info(screen, board, last_move_time)
        pygame.display.flip()

    # Game over message
    result = "Draw" if board.is_stalemate() else "White wins" if not board.turn else "Black wins"
    print(f"Game Over: {result}")

if __name__ == "__main__":
    main()