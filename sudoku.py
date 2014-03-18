from __future__ import print_function
import itertools
import copy

# An implementation based on Peter Norvig's sudoku solver.
# 
# A cell is addressed by a string 'A4', for example.
# A cell's contents are represented by a string of possibilities
# We shall represent a board as a dictionary {cell: string}
# A board can have multiple representations. Its canonical representation is
# the minimal board that cannot be solved further without making deductions
# more sophisticated than "this square only has one possibility left; cross
# out this number from its neighbors"
#
# Significant changes: since we're using a mutable dictionary to alleviate
# the inefficiency of copying a rather large board each time, I used a
# mutable sudokuboard object, whose methods return None.
# This is an essentially cosmetic change.
# Norvig's version handled errors by stuffing both results and errors into
# the return channel; they either returned the successful solve or False.
# I either return the successful solve, or an error will be raised.
# The top-level board.simplify() and board.full_solve() methods will catch
# and deal with those exceptions.

class InvalidBoardState(Exception): pass
class MultipleSolutions(Exception): pass

def cross(aset, bset):
    return tuple(a+b for a in aset for b in bset)

ROWS = 'ABCDEFGHI'
COLUMNS = NUMS = '123456789'
CELLS = sorted(cross(ROWS, COLUMNS))
GROUPS = tuple(itertools.chain(
            (cross(row, COLUMNS) for row in ROWS), 
            (cross(ROWS, col) for col in COLUMNS),
            (cross(rgroup, ngroup) for rgroup in ('ABC', 'DEF', 'GHI') for ngroup in ('123', '456', '789'))))

NEIGHBORHOODS = {cell: tuple(g for g in GROUPS if cell in g) for cell in CELLS}

NEIGHBORS = {cell: set(itertools.chain(*neighborhood)) - {cell} for cell, neighborhood in NEIGHBORHOODS.items()}

assert len(CELLS) == 81
assert len(GROUPS) == 27
print(NEIGHBORHOODS['A1'])
assert NEIGHBORHOODS['A1'] == (('A1','A2','A3','A4','A5','A6','A7','A8','A9'),
                              ('A1','B1','C1','D1','E1','F1','G1','H1','I1'),
                              ('A1','A2','A3','B1','B2','B3','C1','C2','C3'))
assert NEIGHBORS['B1'] == {'B2', 'B3', 'B4', 'B5', 'B6','B7','B8','B9', 'A1','C1','D1','E1','F1','G1','H1','I1', 'A1','C1','A2','B2','C2','A3','B3','C3'}

def process_rawtext(text):
    return ''.join(filter(lambda c: c in '.0123456789', text))

class SudokuBoard:
    def __init__(self, board, debug=False):
        self.board = board
        self.call_count = 0
        self.debug = debug
        self.guess_count = 0

    @classmethod
    def init_from_text(self, processed_text, debug=False):
        assert len(processed_text) == 81
        board = {}
        for i, char in enumerate(processed_text):
            cell = ROWS[i // 9] + COLUMNS[i % 9]
            if char in '.0':
                board[cell] = NUMS
            else:
                board[cell] = char
        return SudokuBoard(board, debug=debug)

    def __copy__(self):
        return SudokuBoard(self.board.copy())

    def __str__(self):
        cell_width = max(len(v) for v in self.board.values()) + 1
        row_divider = '+'.join('-'*(cell_width*3) for i in range(3))
        output = ''
        for r in ROWS:
            output += ''.join(self.board[r+c].center(cell_width)+('|' if c in '36' else '') for c in COLUMNS) + '\n'
            if r in 'CF': 
                output += row_divider + '\n'
        return output

    def simplify(self):
        self.call_count = 0
        try:
            for cell, values in self.board.items():
                if len(values) == 1:
                    self.assign(cell, values)
        except InvalidBoardState:
            print('Simplification failed...')
            print(self)
        print("Called assign or eliminate %s times." % self.call_count)

    def full_solve(self, debug=False):
        if self.is_solved():
            return 

        self.guess_count += 1
        unsolved_cells = filter(lambda c: len(self.board[c]) > 1, CELLS)
        shortest_cell = sorted(unsolved_cells, key=lambda c: len(self.board[c]))[0]

        # All the work is done in the clones, while the original board waits.
        # If the clones get all the way to the end, their progress is copied
        # over onto the original board.
        valid_possibilities = []
        for possibility in self.board[shortest_cell]:
            if debug: print("Attempting to assign %s to %s" % (possibility, shortest_cell))
            clone = copy.copy(self)
            try: 
                clone.assign(shortest_cell, possibility)
                clone.full_solve(debug=debug)
                # If we've gotten to this point, the guess worked.
                valid_possibilities.append(clone)
            except InvalidBoardState, e:
                if debug:
                    print(e)
                    print("Assigning %s to %s led to a contradiction" % (possibility, shortest_cell))
            except MultipleSolutions, e:
                if debug:
                    print(e)
                    print("Found multiple solutions")
            self.guess_count += clone.guess_count

        # At this point, un-clone the board to transfer the successful assignment.
        # If there is no successful clone, we should alert the parent recursion
        # so that they can discard this pathway.
        # If there is more than one successful clone, 

        # Think of the base case - the penultimate assignment.
        # At this point, we have either failed all of the possibilities without
        # further recursion, or we have at least one possibility remaining.

        # Then, if something didn't work, raise the error, 
        # causing the parent recursion to discard the possibility.
        if len(valid_possibilities) == 0:
            raise InvalidBoardState("Uhoh - we bruteforced and found that no possibilities worked!")
        elif len(valid_possibilities) > 1:
            raise MultipleSolutions('\n'.join(map(str, valid_possibilities)))
        else:
            # Yay, we found a unique solution.
            self.board = valid_possibilities[0].board
        print("Made %s guessed assignments before finding the answer" % self.guess_count)

    def is_solved(self):
        return all(len(self.board[cell]) == 1 for cell in CELLS)

    def assign(self, cell, value):
        assert value in NUMS
        assert cell in CELLS
        self.call_count += 1
        if self.debug: print("assigning %s to %s." % (value, cell))
        # if value not in cell possibilities, something's wrong.
        if value not in self.board[cell]:
            raise InvalidBoardState("Attempted to assign value %s to a cell which only had possible values %s" % (cell, str(self.board[cell])))

        # assign, then eliminate this value from all neighbors
        self.board[cell] = value
        for c in NEIGHBORS[cell]:
            self.eliminate(c, value, cell)

    def eliminate(self, cell, value, last_assigned):
        assert value in NUMS
        assert cell in CELLS
        if value in self.board[cell]:
            if self.debug: print("eliminating %s from %s as a result of assigning %s." % (value, cell, last_assigned))
            self.call_count += 1
            self.board[cell] = self.board[cell].replace(value, '')
            if len(self.board[cell]) == 0:
                raise InvalidBoardState("Uhoh - we somehow eliminated the last possible value from a cell")
            # We just figured out a square. Propagate its value.
            if len(self.board[cell]) == 1:
                self.assign(cell, self.board[cell])

            # Also check if we deduced the only possible location in a group
            # for the value we just eliminated
            for neighborhood in NEIGHBORHOODS[cell]:
                if self.debug: print("Testing %s neighborhood to check value %s" %(str(neighborhood), value))
                possible_cells = filter(lambda c: value in self.board[c], neighborhood)
                if self.debug: print("Narrowed down to %s" % str(possible_cells))
                if len(possible_cells) == 0:
                    raise InvalidBoardState("Uhoh, there are no more possible locations for %s in the neighborhood %s" % (value, neighborhood))
                elif len(possible_cells) == 1 and possible_cells[0] != last_assigned:
                    self.assign(possible_cells[0], value)

if __name__ == '__main__':
    import sys
    for line in sys.stdin.readlines():
        sudoku = SudokuBoard.init_from_text(process_rawtext(line))
        sudoku.simplify()
        print(sudoku)
        if not sudoku.is_solved():
            print("Simplifying wasn't enough; attempting DFS bruteforce")
            sudoku.full_solve(debug=True)
            print(sudoku)

