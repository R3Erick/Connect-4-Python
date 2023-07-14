"""
    Program to play connect 4. A 0 is an empty square, a 1 a red piece and a -1
    a yellow one.
"""
import colorama
from copy import deepcopy
import random
import time

MIN_COLUMNS = 4
MAX_COLUMNS = 10
MIN_ROWS = 4
MAX_ROWS = 10

def set_start_board():
    """Return an empty board"""
    return [[0 for m in range(n_columns)] for n in range(n_rows)]

def print_board(board):
    """Print the board, indicating column number"""
    print(" ", *[" {} ".format(n) for n in range(1, n_columns + 1)], " ")
    for row in board:
        print("|", 
           *["({})".format(" " if n == 0 else colorama.Fore.RED + "•" 
                + colorama.Fore.RESET if n == 1 else colorama.Fore.YELLOW 
                + "•" + colorama.Fore.RESET) for n in row], "|")

def start_game():
    """
        Decide the turn order, if the game is played against a cpu or
        another player. Return those values and start the game.
    """
    global n_rows, n_columns
    r_or_y_text = ("\nWelcome to connect 4! (red always starts) Do you want "
        + "to play as red or as yellow? (red = 1) (yellow = -1)  ")
    p_or_cpu_text = ("Do you want to play against another player or against a "
        + "cpu? (other player = 0) (cpu = 1) ")
    
    while True:
        red_or_yellow = input(r_or_y_text)
        if red_or_yellow != "-1" and red_or_yellow != "1":
            print("Choose any of the two options\n")
        else:
            break
    if n_rows == None:
        while True:
            try:
                n_rows = int(input("How many rows should the board have? "))
                if n_rows < MIN_ROWS or n_rows > MAX_ROWS:
                    print("The number of rows must be between 4 and 10\n")
                else:
                    break
            except ValueError:
                print("Introduce a number")
    if n_columns == None:
        while True:
            try:
                n_columns = int(input("And how many columns? "))
                if n_columns < MIN_ROWS or n_columns > MAX_ROWS:
                    print("The number of columns must be between 4 and 10\n")
                else:
                    break
            except ValueError:
                print("Introduce a number")
    while True:
        player_or_cpu = input(p_or_cpu_text)
        if player_or_cpu != "0" and player_or_cpu != "1":
            print("Choose any of the two options\n")
        else:
            break
    board = set_start_board()
    return board, int(red_or_yellow), int(player_or_cpu)

def play_turn(turn, board, p_is_red, against_cpu, turns_played = 0):
    """
        Print the board, ask the player what move does they want to play or move
        the cpu and check if there is any line of 4. If there is one,
        congratulate the winning player/cpu. If not, change the turn and call itself
        until one wins or all the spaces are filled (draw).
    """
    print_board(board)

    if against_cpu:
        input_text = ("Introduce the number of the column in which you want "
            + "to insert the piece: ") 
    else: 
        input_text = ("Turn of the player of the {} pieces. Introduce".format(
            "red" if turn == 1 else "yellow") 
            + " the number of the column in which you want to put the piece: ")
    if against_cpu and (turn == 1 and p_is_red == -1  or turn == -1 and p_is_red == 1):
        print("CPU is thinking...")
        time.sleep(0.75)
        column = cpu_decide(turn, board)
    else:
        try: 
            column = int(input(input_text))   
            if column in range(1, n_columns + 1) and board[0][column - 1] == 0:
                pass # skip into next block
            else:
                print("Introduce the number of an empty column\n")
                play_turn(turn, board, p_is_red, against_cpu, turns_played)
                return        
        except ValueError:
            print("Introduce the number of any of the columns\n")
            play_turn(turn, board, p_is_red, against_cpu, turns_played)
            return

    board = place_piece(turn, column, board)
    win = check_if_win(turn, board, False)
    if win:
        print("")
        print_board(board)
        if not against_cpu:
            print("Victory of the {} pieces player!".format("red" if turn == 1 else "yellow"))
        else:
            if turn == p_is_red:
                print("Victory!")
            else:
                print("Defeat...")
        return

    turns_played += 1
    if turns_played == n_rows * n_columns:
        print("")
        print_board(board)
        print("It's a draw!")
        return
    if turn == 1:
        play_turn(-1, board, p_is_red, against_cpu, turns_played)
    if turn == -1:
        play_turn(1, board, p_is_red, against_cpu, turns_played)

def cpu_decide(turn, board):
    """Decide and return the column in which the cpu will place the piece"""
    win_col = obtain_winning_column(turn, board)
    if win_col:
        return win_col
    lose_col = obtain_winning_column(-1 if turn == 1 else 1, board)
    if lose_col: 
        return lose_col
    make_threat_col = obtain_threat_col(turn, board)
    if make_threat_col:
        return make_threat_col
    defend_threat_col = obtain_threat_col(-1 if turn == 1 else 1, board)
    if defend_threat_col:
        return defend_threat_col
    return choose_random_column(list(range(1, n_columns + 1)), board)


def obtain_winning_column(turn, board):
    """
        Search a column in which, if the player playing puts a piece, they will
        win the game. Return None if there is not any.
    """
    for column in range(1, n_columns + 1):
        copy_board = deepcopy(board)
        if board[0][column - 1] == 0:
            copy_board = place_piece(turn, column, copy_board)
            can_win = check_if_win(turn, copy_board, False)
            if can_win:
                return column
    return None

def obtain_threat_col(turn, board):
    """
        Search a column in which, if the player playing puts a piece, they will
        generate a threat. Return None if there is not any.
    """
    for column in range(1, n_columns + 1):
        copy_board = deepcopy(board)
        if copy_board[0][column - 1] == 0:
            copy_board = place_piece(turn, column, copy_board)
            is_any_threat = check_if_win(turn, copy_board, True)
            if is_any_threat:
                return column
    return None

def choose_random_column(columns, board, std=3):
    """
        Choose a random non-filled column, giving priority to the central ones.
        If the chosen column is filled, the probability of choosing the border
        columns increases, until a column is chosen.
    """
    column = min(max(int(random.gauss(n_columns / 2, n_columns / std)), columns[0]), columns[-1])
    try:
        columns.remove(column)
    except ValueError:
        std += 1 # Encouraging pieces in the border columns
    return column if board[0][column - 1] == 0 else choose_random_column(columns, board, std)

def place_piece(turn, column, board):
    """
        Find the first empty space of a column that is already checked to have
        free spaces to put the piece.
    """
    for n in range(n_rows - 1, -1, -1):
        if board[n][column - 1] == 0:
            board[n][column - 1] = turn
            break
    return board


def check_if_win(turn, board, threat):
    """
        Check if a player has a line. Return True if there is one and False if
        not. If threat is True, also search for threats.
    """
    win_value = turn * 4
    if threat:
        win_value = turn * 3
    max_len = max(n_rows, n_columns)

    for row in range(max_len):
        win_column = []
        for column in range(max_len):
            try:
                if sum([board[(row - n if row - n >= 0 else None)][column + n]
                        for n in range(0, abs(win_value))]) == win_value:
                    return True
            except IndexError:
                pass
            except TypeError:
                pass
            try:
                if sum([board[row + n][column + n] for n in range(0, abs(
                        win_value))]) == win_value:
                    return True
            except IndexError:
                pass
            try:     
                (win_column.append(board[column][row]) if board[column][row] 
                    == win_value / abs(win_value) else win_column.clear())
                if abs(win_value) == len(win_column):
                    return True
            except IndexError:
                pass
            try:    
                if board[row].count(0) > n_columns - abs(win_value):
                    continue
                pieces_sum = sum(board[row][column:column + abs(win_value)])
                if pieces_sum == win_value:
                    return True
            except IndexError:
                pass
    return False

def ask_play_again(winner):
    """
       Core of the program once the first game finishes. Ask the player if they
       want to play again. If not, exit the program.
    """
    play_again = input("Do you want to play again? (yes = 1, no = 0) ")
    if play_again == "1":
        board, p_is_red, against_cpu = start_game()
        winner = play_turn(1, board, p_is_red, against_cpu) # Red always starts
        ask_play_again(winner)
    elif play_again == "0":
        quit("Play again anytime!")
    else:
        print("Choose any of the two options")
        ask_play_again(winner)

if __name__ == "__main__":
    n_rows = None
    n_columns = None
    colorama.init(autoreset=True)

    board, p_is_red, against_cpu = start_game()
    winner = play_turn(1, board, p_is_red, against_cpu) # Red always starts
    ask_play_again(winner)