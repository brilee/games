from string import ascii_lowercase as letters
import random

with open('/usr/share/dict/words') as f:
    DICTIONARY = set(line.strip().upper() for line in f.readlines())

def display(board):
    print 'Board is:'
    for row in board:
        print row
    return None

def possibilities(position, BS, diagonals=True, toroidal=False):
    '''Enumerates the 8 possibilities for next position,
    excluding the starting position
    '''
    # unpack position 2-tuple
    i, j = position 
    # This version disallows board wraps
    if not diagonals:
        offsets = [(1,0), (-1, 0), (0, 1), (0, -1)]
    else:
        offsets = [(1,1), (1,0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]

    all_possibilities = [(i+k, j+l) for (k, l) in offsets]
    if toroidal:
        all_possibilities = [(i%BS, j%BS) for i,j in all_possibilities]

    return [(i,j) for (i,j) in all_possibilities if 0<=i<BS and 0<=j<BS] 

def translate(sequence, board):
    ''' Takes a path on the board and converts it into its string representation'''
    return ''.join(board[i][j] for (i,j) in sequence)

def search(board, length, **kwargs):
    ''' Searches the board for all words that are $length long.'''
    # assume square board
    BS = len(board)
    board = [row.upper() for row in board]
    # Internally a path is represented by a list of 2-tuples:
    # [(1,1), (1,2), (1,3), (2,3)... etc]

    # Possible start positions, formatted as a 1-path
    paths = [[(i,j)] for i in range(BS) for j in range(BS)]

    for i in range(length - 1):
        # Recursively build up new possibilities, pruning at each step
        # the paths that self-intersect.
        paths = [path + [possibility] for path in paths for possibility in possibilities(path[-1], BS, **kwargs)]
        # This weeds out self-intersecting paths.
        paths = [p for p in paths if len(set(p)) == len(p)]

    words = [translate(path, board) for path in paths]
    valid_words = filter(lambda word: word in DICTIONARY, words)

    # Only print unique hits
    return set(valid_words)
    
if __name__ == '__main__':
    BS = 7
    board = [''.join(random.choice(letters) for i in range(BS)) for j in range(BS)]
    display(board)
    print search(board, 4, toroidal=False, diagonals=False)

