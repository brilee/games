from __future__ import print_function

import random
from collections import Counter

# A knock-off of the game "Threes", except instead of combining 
# like numbers to make their double, you combine adjacent fibonacci numbers
# to make the next fibonacci number.
# Written by Brian Lee

def fibonacci_gen(n):
    'Generates fibonacci numbers, starting with 1, 2'
    result = []
    a, b = 1, 2
    for i in range(n):
        result.append(a)
        a, b = b, a+b
    return result


BOARD_SIZE = 4
# character to denote an empty slot on the board
EMPTY = ' '
# The empty board.
EMPTY_BOARD = tuple((EMPTY,)*BOARD_SIZE for i in range(BOARD_SIZE))
# A list of fibonacci numbers. Should be impossible to get a piece bigger than this.
FIBS = fibonacci_gen(3 * BOARD_SIZE**2)
# scoring at the end: F_n yields 2**n points.
SCORES = {fib : 2**i for i, fib in enumerate(FIBS)}
# special case for combining 1 + 1 = 2
COMBOS = {(1,1) : 2}
# normal case: F_{n-2} + F_{n-1} = F_n
COMBOS.update({(FIBS[i], FIBS[i+1]) : FIBS[i+2] for i in range(len(FIBS) - 2)})
COMBOS.update({(FIBS[i+1], FIBS[i]) : FIBS[i+2] for i in range(len(FIBS) - 2)})

def rotateCW(board): return tuple(map(tuple, zip(*board[::-1])))
def rotate180(board): return rotateCW(rotateCW(board))
def rotateCCW(board): return rotateCW(rotateCW(rotateCW(board)))
testboard = ((1,2,3), (4,5,6), (7,8,9))
assert rotateCW(testboard) == ((7,4,1), (8,5,2), (9,6,3))
assert rotateCW(rotateCW(rotateCW(rotateCW(testboard)))) == testboard

def leftshift(row):
    '''
    Takes a tuple (1,3,5,8) and returns its left-shift: (1,8,8,EMPTY)
    If no shift is possible, return tuple unchanged.
    '''
    new_row = list(row)
    for i in range(len(row) - 1):
        if row[i] == EMPTY:
            new_row[i:-1] = row[i+1:]
            new_row[-1] = EMPTY
            break
        if (row[i], row[i+1]) in COMBOS:
            new_row[i] = COMBOS[(row[i], row[i+1])]
            new_row[i+1:-1] = row[i+2:]
            new_row[-1] = EMPTY
            break
    return tuple(new_row)

assert leftshift((1,3,5,8)) == (1,8,8,EMPTY)
assert leftshift((1,3,8,21)) == (1,3,8,21)
assert leftshift((EMPTY,1,1,2)) == (1,1,2,EMPTY)
assert leftshift((1,EMPTY, 1,2)) == (1,1,2,EMPTY)
assert leftshift((1,3,8,EMPTY)) == (1,3,8,EMPTY) 

def new_board():
    'Customize the starting board here.'
    return EMPTY_BOARD

def board_iter(board):
    'Iterates over nonempty elements of the board'
    return (item for row in board for item in row if item != EMPTY)

def power_rand(p, lower, upper): 
    '''
    Power law distributed random numbers, flipped so that early numbers are
    more frequent.
    http://mathworld.wolfram.com/RandomNumber.html
    '''
    return ((upper**(p+1) - lower**(p+1)) * random.random() + lower**(p+1)) ** (1/(p+1))

def get_new_fib(board):
    '''
    Returns a random new fibonacci number. 
    If the highest number on board is 21, can return fibs up to 8.
    1 and 2 are always possibilities.
    '''
    if board == EMPTY_BOARD:
        index = 2
    else:
        highest_number = max(board_iter(board))
        index = FIBS.index(highest_number)
    # The largest fibonacci F_index that we are going to produce.
    max_index = max(2, index - 2) 

    # Use a power law to weight the random tiles towards the smaller numbers.
    # The likelyhood of the tile F_n is proportional to n^p.
    p = -1.5
    # offset by 1 and subtract later because power laws blow up at 0.
    lower = 1
    # we want an upper-inclusive range, so add another 1.
    upper = max_index + 2

    return FIBS[int(power_rand(p, lower, upper)) - 1]

def move_left(board, next_piece):
    '''
    Takes a board and returns the entire board left-shifted with a new tile.
    If no shift is possible, return the board unchanged.
    '''
    moved_board = [leftshift(row) for row in board]
    if tuple(moved_board) == board and board != EMPTY_BOARD:
        return board
    else:
        for i in range(BOARD_SIZE):
            if moved_board[i][-1] == EMPTY:
                moved_board[i] = moved_board[i][:-1] + (next_piece,)
                break
    return tuple(moved_board)

def move_right(board, next_piece):
    return rotate180(move_left(rotate180(board), next_piece))

def move_up(board, next_piece):
    return rotateCW(move_left(rotateCCW(board), next_piece))

def move_down(board, next_piece):
    return rotateCCW(move_left(rotateCW(board), next_piece))

move_dispatch = {'w': move_up,
                 'a': move_left,
                 'd': move_right,
                 's': move_down}

def is_valid(move, board):
    # When a board is empty, it gives a false positive for "move made"
    return board == EMPTY_BOARD or move_dispatch[move](board, EMPTY) != board

def check_loss(board):
    '''
    Checks if the board is a lost position. 
    A board is lost when no more moves can be made.
    '''
    return not any(is_valid(move, board) for move in move_dispatch)

def print_board(board):
    if board == EMPTY_BOARD:
        width = 1
    else:
        width = max(len(str(piece)) for piece in board_iter(board))

    # !s means convert to string before printing
    # > means right-aligned
    # :4s means 4-char fixed-width
    cell_template = '{!s:>' + str(width) + 's}'
    row_separator = ('-'*width).join(['\n'] + ['.']*(len(board)-1) + ['\n'])
    rows = row_separator.join('|'.join(cell_template.format(c) for c in row) for row in board)
    print(rows)

def score_board(board):
    return sum(SCORES[num] for num in board_iter(board))

def print_score_breakdown(board):
    counts = Counter(board_iter(board))
    row_template = ' | '.join('{:^6s}' for i in range(4))
    print(row_template.format('Tile', 'Number', 'Value', 'Score'))
    for tile in sorted(counts):
        print(row_template.format(
                    str(tile), 
                    str(counts[tile]), 
                    str(SCORES[tile]), 
                    str(counts[tile] * SCORES[tile])
                    ))
    print(row_template.format('', '', 'Total:', str(score_board(board))))


# http://code.activestate.com/recipes/134892/
class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

getch = _Getch()

def play_game():
    ' Plays a game of Fibs. Returns False if the user quit.'
    board = new_board()
    while True:
        print_board(board)
        print("Score: %s" % score_board(board))
        next_piece = get_new_fib(board)
        print("Upcoming tile: %s" % next_piece)
        print('make a move (wasd / q to quit)')

        move = '?'
        while not (move == 'q'
                   or (move in 'wasd'
                       and is_valid(move, board))):
             move = getch()
        if move == 'q':
            return False
        board = move_dispatch[move](board, next_piece)
        if check_loss(board):
            print("No more moves available! You lose.")
            print_score_breakdown(board)
            return True

if __name__ == "__main__":
    print("Welcome to Fibs! To play: 'squash' two adjacent Fibonacci numbers together to make the next one!")
    while True:
        success = play_game()
        if success:
            print("Play again? y/n")
            play_again = '?'
            while play_again not in 'yn':
                play_again = getch()
            if play_again == 'y':
                continue
            else:
                break
        else:
            break
