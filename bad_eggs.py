from __future__ import print_function

import math

MAP_WIDTH = 40
MAP_HEIGHT = 20
GRAVITY = -5 # pixels per time squared
EXPLOSION_RADIUS = 3

MAP = [int(MAP_HEIGHT / 2)] * MAP_WIDTH


class Player():
    def __init__(self, x_position):
        self.hp = 100
        self.x = int(x_position)

    def isAlive(self):
        return self.hp > 0

    def fireProjectile(self):
        angle = float(raw_input('What angle do you want to fire at? (0 = right, 180 = left, 90 = up)\n')) * math.pi / 180
        power = float(raw_input('What power do you want to fire with? (Pick a number between 0 and 20)\n'))
        # a projectile is a dict with keys (x, y, angle, power)
        return {'x':self.x, 'y':MAP[self.x], 'angle':angle, 'power':power}
    
    def applyDamage(self, impact_center):
        self.hp -= int(20 * math.exp(-0.15 * math.sqrt((self.x - impact_center[0])**2 
                                         + (MAP[self.x] - impact_center[1])**2)))
    

def refresh_view(MAP, player1, player2, projectile_path=None):
    map_vertical_strips = [['@'] * height + [' '] * (MAP_HEIGHT - height) for height in MAP]

    def assign_pixel(x, y, character):
        if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
            map_vertical_strips[x][y] = character

    if projectile_path:
        # map is still in [x,y] orientation
        for point in projectile_path:
            assign_pixel(point[0], point[1], '.') 
            
    for p in (player1, player2):
        assign_pixel(p.x, MAP[p.x], 'T')

    map_horizontal_strips = [''.join(strip) for strip in zip(*map_vertical_strips)] # clever trick for transposing a matrix
    
    for hstrip in reversed(map_horizontal_strips):
        print(hstrip)
    print('Player 1 HP: %s     Player 2 HP: %s' % (player1.hp, player2.hp))

def compute_impact(projectile, MAP):
    x_pos = projectile['x']
    y_pos = projectile['y']
    power = projectile['power']
    angle = projectile['angle']
    x_vel = power * math.cos(angle)
    y_vel = power * math.sin(angle)
    
    projectile_path = set()

    delta_t = .01
    while 0 < x_pos < MAP_WIDTH and y_pos >= MAP[int(x_pos)]:
        x_pos += delta_t * x_vel
        y_pos += delta_t * y_vel
        y_vel += delta_t * GRAVITY
        projectile_path.add((int(x_pos), int(y_pos)))
    
    return (x_pos, y_pos), projectile_path
    

def apply_explosion(impact_center, MAP):
    x = int(impact_center[0])
    y = impact_center[1]
    m = MAP[:]
    for i in range(-EXPLOSION_RADIUS, EXPLOSION_RADIUS + 1):
        if 0 <= x + i < MAP_WIDTH:
            MAP[x + i] = int(min(MAP[x + i], y - math.sqrt(EXPLOSION_RADIUS**2 - i **2)))
    return MAP

player1 = Player(int(MAP_WIDTH*.1))
player2 = Player(int(MAP_WIDTH*.9))


turn = 1
refresh_view(MAP, player1, player2)
while player1.isAlive() and player2.isAlive():
    if turn == 1:
        print('Player 1\'s turn')
        projectile = player1.fireProjectile()
    else:
        print('Player 2\'s turn')
        projectile = player2.fireProjectile()
    turn *= -1

    impact_center, projectile_path = compute_impact(projectile, MAP)
    MAP = apply_explosion(impact_center, MAP)
    for p in (player1, player2):
        p.applyDamage(impact_center)
    refresh_view(MAP, player1, player2, projectile_path)

print('Player %s wins!' % (1 if player1.isAlive() else 2))
