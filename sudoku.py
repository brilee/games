# Sudoku puzzle input format:
# 9 lines of 9digits, no separation. 0 indicates unknown
#
# TODO:
# Implement more intelligent guessing

from copy import deepcopy
import time

separators = ((0,1,2),(3,4,5),(6,7,8))
all_values = ('1','2','3','4','5','6','7','8','9')

class SudokuBoard(object):
    '''
    A board. Internally represented as a 9x9 list of lists. loc is a tuple
    (i,j), refers to i_th row, j_th column. 
    '''
    
    def __init__(self,values):
        '''input value should be a list of lists.'''
        self.board = values
        self.inverted_board = list(zip(*self.board))
##        self.rows = list(set(numbers for numbers in row) for row in self.board)
##        self.columns = list(set(numbers for numbers in column) for column in self.inverted_board)
##        self.squares = []
##        for groupR in separators:
##            for groupC in separators:
##                square = set()
##                for i in groupR:
##                    for j in groupC:
##                        square.add(self.board[i][j])
##                self.squares.append(square)

    def get_value(self,loc):
        return self.board[loc[0]][loc[1]]
                                
    def get_possibilities(self,loc):
        def get_row(i):
            return set(number for number in self.board[i])
        def get_column(j):
            return set(number for number in self.inverted_board[j])
        def get_square(i,j):
            row_index = i//3
            column_index = j//3
            square = set()
            for row in separators[row_index]:
                for column in separators[column_index]:
                    square.add(self.board[row][column])
            return square
        i = loc[0]
        j = loc[1]
        if self.board[i][j] != '0':
            return self.board[i][j]
        all_numbers = set().union(get_row(i),get_column(j),get_square(i,j))
        poss = []
        for number in all_values:
            if number not in all_numbers:
                poss.append(number)
        if poss == []:
            return False
        else:
            return poss
    
    def find_empty(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == '0':
                    return (i,j)
        return False

#    def optimize_board(self):
#        optimized = False
#        while not optimized:
            #
            #
            #
            #
            #
            
        
    def make_move(self,loc,num):
        newboard = deepcopy(self.board)
        newboard[loc[0]][loc[1]] = num
        return SudokuBoard(newboard)

    def print_board(self):
        # for debugging and final output
        rep = ['']*9
        for i in range(9):
            for j in range(9):
                rep[i] += str(self.board[i][j])
                if j%3 == 2 and j != 8:
                    rep[i] += '[]'
        rep.insert(6,'===  ===  ===')
        rep.insert(3,'===  ===  ===')
        for row in rep:
            print(row)

def create_board(lines):
    # takes any indexable matrix and converts into a board
    board = []
    for line in lines:
        board.append(list(number for number in line))
    new_board = SudokuBoard(board)
    return new_board

def solve_sudoku(startingboard):
    itercount = 0
    checkpoint = time.time()
    stack = [startingboard]
    while stack != []:
        itercount += 1
        next_board = stack.pop(-1)
        next_empty = next_board.find_empty()
        if next_empty == False: # The sudoku is filled in completely
            print('Original board was:')
            startingboard.print_board()
            print('\nSolved board:')
            next_board.print_board()
            print('Took ',itercount,'iterations')
            print('Took ',time.time() - checkpoint, 'seconds')
            break
        poss = next_board.get_possibilities(next_empty)
        #print(poss)
        #if poss == False:
        #   print('Dead end reached')
        if poss != False: # If false, at least one guess was incorrect
            for num in poss:
                newboard = next_board.make_move(next_empty,num)
                stack.append(newboard)
        
def solve_manual_input_sudoku():
    data = []
    while len(data) < 9:
        valid = False
        while valid == False:
            print('Enter row', len(data)+1, '. Blanks are indicated by a 0')
            x = input()
            if len(x) == 9:
                valid = True
            else:
                print('You didn\'t input a 9-digit string')
        data.append(list(x))
    board = SudokuBoard(data)
    solve_sudoku(board)
    

testdata = ['003020600','900305001','001806400','008102900','700000008',
           '006708200','002609500','800203009','005010300']
testboard = create_board(testdata)
solve_sudoku(testboard)

#solve_manual_input_sudoku()
