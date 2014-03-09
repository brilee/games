# Solves a word search puzzle with build-in word dictionary.

with open('/usr/share/dict/words') as f:
    WORDS = set(line.strip().upper() for line in f.readlines())

def flip_horizontal(puzzle):
    return [row[::-1] for row in puzzle]

def flip_vertical(puzzle):
    return puzzle[::-1]

def flip_diagonal(puzzle):
    return [''.join(letters) for letters in zip(*puzzle)]

def rotate_180(puzzle):
    return flip_vertical(flip_horizontal(puzzle))

# Straights
def generate_horizontal(puzzle, min_length):
    len_row = len(puzzle[0])
    return [row[i:j] for row in puzzle
                     for i in range(len_row)
                     for j in range(len_row)
                     if (i < j and j - i >= min_length)]

def generate_vertical(puzzle, min_length):
    return generate_horizontal(flip_diagonal(puzzle), min_length)

def generate_horizontal_backwards(puzzle, min_length):
    return generate_horizontal(flip_horizontal(puzzle), min_length)

def generate_vertical_backwards(puzzle, min_length):
    return generate_vertical(flip_vertical(puzzle), min_length)

# Diagonals
def generate_down_right_diagonals(puzzle, min_length):
    def cycle(string, n):
        return string[n:] + string[:n]
    def realign_puzzle(puzzle):
        return [cycle(row, i) for i, row in enumerate(puzzle)]
    
    transformed = flip_diagonal(realign_puzzle(puzzle))

    # now we can just generate horizontal strings, while being
    # careful to exclude strings that would have crossed boundaries
    # in the original untransformed puzzle.

    # ######
    # %X*XX%
    # %XX*X%
    # %XXX*%
    # %XXXX%
    # ######

    # gets transformed to

    # #XXXX#
    # #***%#
    # #XX%%#
    # #X%%X#
    # #%%XX#
    # #%XXX#

    # Draw a diagonal from bottom left to top right. Any elements on this
    # diagonal or above it are in sector A. Any elements below it are sector B.
    # A horizontal word that stays entirely in one sector is a valid word in
    # the untransformed puzzle.
    len_row = len(puzzle[0])
    def sector(location):
        return location[0] + location[1] < len_row

    def XNOR(sector1, sector2):
        return (sector1 and sector2) or (not sector1 and not sector2)

    return [row[c1:c2] for k, row in enumerate(transformed)
                 for c1 in range(len_row)
                 for c2 in range(len_row)
                 if (c1 < c2 
                    and c2 - c1 >= min_length
                    and (XNOR(sector([c1,k]), sector([c2-1, k]))))]

def generate_down_left_diagonals(puzzle, min_length):
    return generate_down_right_diagonals(flip_horizontal(puzzle), min_length)

def generate_up_right_diagonals(puzzle, min_length):
    return generate_down_right_diagonals(flip_vertical(puzzle), min_length)

def generate_up_left_diagonals(puzzle, min_length):
    return generate_down_right_diagonals(rotate_180(puzzle), min_length)

def is_valid_word(word):
    return word in WORDS

def solve_crossword(puzzle, diagonals=True, reverse=True, min_length=4):
    answers = []
    answers.extend(filter(is_valid_word, generate_horizontal(puzzle, min_length)))
    answers.extend(filter(is_valid_word, generate_vertical(puzzle, min_length)))

    if reverse:
        answers.extend(filter(is_valid_word, generate_vertical_backwards(puzzle, min_length)))
        answers.extend(filter(is_valid_word, generate_horizontal_backwards(puzzle, min_length)))
    if diagonals:
        answers.extend(filter(is_valid_word, generate_down_right_diagonals(puzzle, min_length)))
        answers.extend(filter(is_valid_word, generate_up_left_diagonals(puzzle, min_length)))
        answers.extend(filter(is_valid_word, generate_up_right_diagonals(puzzle, min_length)))
        answers.extend(filter(is_valid_word, generate_down_left_diagonals(puzzle, min_length)))
    return answers


if __name__ == '__main__':

    puzzle = '''CDAPMDXC
SJXXLHUK
YHNRVMIO
GMORZTLM
QWBITLHL
JHDIEKGW
FSEHQBZV
SSENETUC'''.split()

    print solve_crossword(puzzle, diagonals=True, reverse=True)
