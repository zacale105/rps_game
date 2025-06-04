'''
This is a simple Rock Paper Scissors game with a twist.
You need to win 3 games in a row to unlock Tic Tac Toe.

The game is hosted at https://rockpaperscissors.onrender.com/

The code is hosted at https://github.com/yourusername/your-repo
'''
from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# List of possible choices for Rock Paper Scissors
CHOICES = ['rock', 'paper', 'scissors']

# Game state
rps_wins = 0  # Track number of wins in Rock Paper Scissors
WINS_REQUIRED = 3  # Number of wins required to unlock Tic Tac Toe

# Tic Tac Toe game state
tictactoe_board = None
current_player = None
game_mode = None

def initialize_board():
    global tictactoe_board, current_player
    tictactoe_board = ['' for _ in range(9)]
    current_player = 'X'

def determine_winner(player_choice, computer_choice):
    if player_choice == computer_choice:
        return "It's a tie!"
    elif (
        (player_choice == 'rock' and computer_choice == 'scissors') or
        (player_choice == 'paper' and computer_choice == 'rock') or
        (player_choice == 'scissors' and computer_choice == 'paper')
    ):
        return "You win!"
    else:
        return "Computer wins!"

def check_winner(board):
    # Check rows, columns and diagonals
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]  # Diagonals
    ]
    
    for combo in winning_combinations:
        if board[combo[0]] and board[combo[0]] == board[combo[1]] == board[combo[2]]:
            return board[combo[0]]
    
    if '' not in board:
        return 'tie'
    return None

def get_computer_move(board):
    empty_cells = [i for i, cell in enumerate(board) if cell == '']
    if empty_cells:
        return random.choice(empty_cells)
    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/tictactoe')
def tictactoe():
    return render_template('tictactoe.html')

@app.route('/play', methods=['POST'])
def play():
    global rps_wins
    player_choice = request.json.get('choice')
    if player_choice not in CHOICES:
        return jsonify({'error': 'Invalid choice'}), 400
    
    # If already won 3 games, return without playing
    if rps_wins >= WINS_REQUIRED:
        return jsonify({
            'computer_choice': '',
            'result': 'You have already unlocked Tic Tac Toe! Click the button below to play.',
            'wins': rps_wins,
            'tictactoe_unlocked': True
        })
    
    computer_choice = random.choice(CHOICES)
    result = determine_winner(player_choice, computer_choice)
    
    # Update win counter but cap it at 3
    if result == "You win!" and rps_wins < WINS_REQUIRED:
        rps_wins += 1
    
    return jsonify({
        'computer_choice': computer_choice,
        'result': result,
        'wins': rps_wins,
        'tictactoe_unlocked': rps_wins >= WINS_REQUIRED
    })

@app.route('/check_unlock', methods=['GET'])
def check_unlock():
    return jsonify({
        'wins': rps_wins,
        'tictactoe_unlocked': rps_wins >= WINS_REQUIRED
    })

@app.route('/tictactoe/start', methods=['POST'])
def start_tictactoe():
    global game_mode
    game_mode = request.json.get('mode')
    initialize_board()
    return jsonify({
        'board': tictactoe_board,
        'current_player': current_player
    })

@app.route('/tictactoe/play', methods=['POST'])
def play_tictactoe():
    global tictactoe_board, current_player
    
    if not tictactoe_board:
        return jsonify({'error': 'Game not started'}), 400
    
    position = request.json.get('position')
    if not (0 <= position <= 8) or tictactoe_board[position]:
        return jsonify({'error': 'Invalid move'}), 400
    
    # Player move
    tictactoe_board[position] = current_player
    winner = check_winner(tictactoe_board)
    
    response_data = {
        'board': tictactoe_board,
        'last_move': position,
        'current_player': current_player
    }
    
    if winner:
        response_data['winner'] = winner
        return jsonify(response_data)
    
    # Switch player
    current_player = 'O' if current_player == 'X' else 'X'
    response_data['current_player'] = current_player
    
    # If playing against computer and it's computer's turn
    if game_mode == 'computer' and current_player == 'O':
        computer_move = get_computer_move(tictactoe_board)
        if computer_move is not None:
            tictactoe_board[computer_move] = 'O'
            winner = check_winner(tictactoe_board)
            current_player = 'X'  # Switch back to player
            response_data.update({
                'board': tictactoe_board,
                'computer_move': computer_move,
                'current_player': current_player
            })
            if winner:
                response_data['winner'] = winner
    
    return jsonify(response_data)

@app.route('/reset', methods=['POST'])
def reset_game():
    global rps_wins, tictactoe_board, current_player, game_mode
    # Reset all game states
    rps_wins = 0
    tictactoe_board = None
    current_player = None
    game_mode = None
    return jsonify({
        'wins': rps_wins,
        'tictactoe_unlocked': False,
        'message': 'Game reset successfully'
    })

if __name__ == '__main__':
    app.run(debug=True) 