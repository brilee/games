from __future__ import print_function
from collections import namedtuple
import math
from copy import deepcopy

MAP_WIDTH = 40
MAP_HEIGHT = 20
GRAVITY = -5 # pixels per time squared
EXPLOSION_RADIUS = 3

Projectile = namedtuple('Projectile', ['x', 'y', 'angle', 'power'])
Point = namedtuple('Point', ['x', 'y'])
# ProjectilePath = set(Point)

class Player():
    def __init__(self, x_position):
        self.hp = 100
        self.x = int(x_position)

    def isAlive(self):
        return self.hp > 0

    def fireProjectile(self, board):
        angle = float(raw_input('What angle do you want to fire at? (0 = right, 180 = left, 90 = up)\n')) * math.pi / 180
        power = float(raw_input('What power do you want to fire with? (Pick a number between 0 and 20)\n'))
        return Projectile(x=self.x, y=board[self.x], angle=angle, power=power)
    
    def applyDamage(self, impact_center, board):
        self.hp -= int(20 * math.exp(-0.15 
            * math.sqrt((self.x - impact_center[0])**2 
                        + (board[self.x] - impact_center[1])**2)))

    def position(self, board):
        return Point(self.x, board[self.x])


def refresh_view(board, player1, player2, projectile_path=None):
    map_vertical_strips = [['@'] * height + [' '] * (MAP_HEIGHT - height) for height in board]

    def assign_pixel(point, character):
        x, y = int(round(point.x)), int(round(point.y))
        if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
            map_vertical_strips[x][y] = character

    if projectile_path:
        # board is still in [x,y] orientation
        for point in projectile_path:
            assign_pixel(point, '.') 
            
    for player in (player1, player2):
        assign_pixel(player.position(board), 'T')

    # clever trick for transposing a matrix
    map_horizontal_strips = [''.join(strip) 
        for strip in zip(*map_vertical_strips)] 

    for hstrip in reversed(map_horizontal_strips):
        print(hstrip)
    print('Player 1 HP: %s     Player 2 HP: %s' % (player1.hp, player2.hp))

def compute_impact(projectile, board):
    'Performs euler integration to determine projectile path and impact point.'
    x = projectile.x
    y = projectile.y
    power = projectile.power
    angle = projectile.angle
    v_x = power * math.cos(angle)
    v_y = power * math.sin(angle)
    
    # Using a set allows us to do a fine-grained simulation while
    # only keeping unique points at the end.
    projectile_path = set()

    dt = .01
    while 0 < x < MAP_WIDTH and y >= board[int(x)]:
        x += dt * v_x
        y += dt * v_y
        v_y += dt * GRAVITY
        projectile_path.add(Point(int(round(x)), int(round(y))))
    
    return (x, y), projectile_path
    
def apply_explosion(impact_center, board):
    '''Returns a board with a circular explosion carved out. 
    Any land above the explosion is removed. '''
    x = int(impact_center[0])
    y = impact_center[1]
    board = deepcopy(board)
    for i in range(-EXPLOSION_RADIUS, EXPLOSION_RADIUS + 1):
        if 0 <= x + i < MAP_WIDTH:
            board[x + i] = int(min(board[x + i], y - math.sqrt(EXPLOSION_RADIUS**2 - i **2)))
    return board

player1 = Player(int(MAP_WIDTH*.1))
player2 = Player(int(MAP_WIDTH*.9))


if __name__ == '__main__':
    board = [int(MAP_HEIGHT / 2)] * MAP_WIDTH
    player1turn = True
    refresh_view(board, player1, player2)
    while player1.isAlive() and player2.isAlive():
        if player1turn:
            print('Player 1\'s turn')
            projectile = player1.fireProjectile(board)
        else:
            print('Player 2\'s turn')
            projectile = player2.fireProjectile(board)
        player1turn = not player1turn

        impact_center, projectile_path = compute_impact(projectile, board)
        board = apply_explosion(impact_center, board)
        for p in (player1, player2):
            p.applyDamage(impact_center, board)
        refresh_view(board, player1, player2, projectile_path)

    print('Player %s wins!' % (1 if player1.isAlive() else 2))
