from __future__ import print_function

PUZZLE_SIZE = 5

class HanoiPuzzle():
    '''
    Has a single variable self.stacks, which is a list of three lists of
    integers from 1...PUZZLE_SIZE representing the various pieces.
    Each of the three lists should be descending, and each integer
    should be in only one list.

    The three stacks are given indices 0, 1, and 2.
    '''
    def __init__(self, PUZZLE_SIZE, randomize=False):
        '''
        Initializes a Hanoi puzzle.
        Pass the kwarg randomize=True in order to initialize with a random
        valid configuration.
        '''
        self.size = PUZZLE_SIZE
        if randomize:
            import random
            stack_allocation = (random.choice('012') for i in range(PUZZLE_SIZE))
            self.stacks = [[], [], []]
            for i, index in enumerate(stack_allocation):
                self.stacks[int(index)].append(PUZZLE_SIZE - i)
        else:
            self.stacks = [list(range(PUZZLE_SIZE, 0, -1)), [], [],]

    def __str__(self):
        output = ''
        for stack in self.stacks:
            output += ('::' + ' '.join(str(n) for n in stack) + '\n')
        output += '\n'
        return output

    def verify(self):
        '''
        Verify that current state of puzzle is valid.
        '''
        import itertools
        assert set(itertools.chain(self.stacks)) == set(range(1, PUZZLE_SIZE + 1))
        for s in self.stacks:
            assert sorted(s, reverse=True) == s
        assert sum(map(len, self.stacks)) == self.size
        return True

    def move(self, index1, index2, verbose=False):
        '''
        Moves the top piece from stack index1 to stack index2
        '''
        stack1 = self.stacks[index1]
        stack2 = self.stacks[index2]

        # stack1 should contain something, and stack2 should
        # either be empty or able to accommodate piece from stack1.
        if stack1 and (not stack2 or stack1[-1] < stack2[-1]):
            stack2.append(stack1.pop())
            if verbose:
                print(self)
        else:
            print('Invalid move from stack %s to stack %s' % (index1, index2) )

    def move_n(self, n, index1, index2, **kwargs):
        '''
        Move the top n disks from stack1 to stack2.
        Assumes that the top n disks are consecutively sized!
        Algorithm:
        Move the top n-1 disks from stack1 to stack3.
        Move the n-disk from stack1 to stack2.
        Move the top n-1 disks from stack3 to stack2.

        If we make the assumption that top n disks are consecutive,
        we will always be able to recursively do the smaller case without
        worrying if the smaller one is possible.
        '''
        assert n <= self.size
        if index1 == index2:
            return        
        if n == 1:
            self.move(index1, index2, **kwargs)
        else:
            # the three stacks are 0, 1, 2.
            # given any two, you can compute the third stack by saying
            # 3 - index1 - index2.
            self.move_n(n-1, index1, 3-index1-index2, **kwargs)
            self.move(index1, index2, **kwargs)
            self.move_n(n-1, 3-index1-index2, index2, **kwargs)

    def solve_basic_hanoi(self, **kwargs):
        'Just for demonstration purposes.'
        self.move_n(self.size, 0, 1, **kwargs)       

    def solve(self, **kwargs):
        '''
        Solves an arbitrary Hanoi puzzle instance.
        Algorithm:
        Start with the 1-disk. Move it onto the 2-disk if is exposed;
        if the 2-disk is not exposed, then it must already be under the 1-disk.
        Then, recursively move the completed n-stack onto the (n+1)-disk.
        '''
        def find_piece(piece_size):
            assert piece_size <= self.size
            for i in range(3):
                if piece_size in self.stacks[i]:
                    return i

        for i in range(1, self.size):
            a, b = find_piece(i), find_piece(i+1)
            self.move_n(i, a, b, **kwargs)
            

if __name__ == '__main__':
    hanoi = HanoiPuzzle(PUZZLE_SIZE, randomize=True)
    print(hanoi)
    hanoi.solve(verbose=True)
    print(hanoi)
