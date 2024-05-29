import pygame as pg
import numpy as np
from settings import *
from numba import njit, prange

class Mode7:
    def __init__(self,app):
        self.app = app

        #Loads floor texture, converts it, and gets its size
        self.floor_tex = pg.image.load('Floor.jpeg').convert()
        self.tex_size = self.floor_tex.get_size()

        #Same idea just for the roof
        self.ceil_tex = pg.image.load('roof.png').convert()
        self.ceil_tex = pg.transform.scale(self.ceil_tex, self.tex_size)
        self.ceil_array = pg.surfarray.array3d(self.ceil_tex)

        #Creates a floor and screen surfarrays
        self.floor_array = pg.surfarray.array3d(self.floor_tex)
        self.screen_array = pg.surfarray.array3d(pg.Surface(WIN_RES))

        self.alt = 1.0
        self.angle = 0.0
        self.pos = np.array([0.0, 0.0])

    def update(self):
        #Player movement
        self.movement()
        self.screen_array = self.render_frame(self.floor_array, self.ceil_array, self.screen_array,
                                              self.tex_size, self.angle, self.pos, self.alt)

    @staticmethod
    @njit(fastmath = True, parallel = True)
    def render_frame(floor_array, ceil_array, screen_array, tex_size, angle, player_pos, alt):

        sin, cos = np.sin(angle), np.cos(angle)

        #Iterates through the entire screen array
        for i in prange(WIDTH):
            new_alt = alt
            for j in range(HALF_HEIGHT, HEIGHT):
                x = HALF_WIDTH - i
                y = j + FOCAL_LEN
                z = j - HALF_HEIGHT + 0.01

                #rotation
                px = (x * cos - y * sin)
                py = (x * sin + y * cos)

                #Floor projection and transformation
                floor_x = px / z - player_pos[1]
                floor_y = py /z +player_pos[0]

                floor_pos = int(floor_x * SCALE % tex_size[0]), int(floor_y * SCALE % tex_size[1])
                floor_col = floor_array[floor_pos]

                # ceil projection and transformation
                ceil_x = alt * px / z - player_pos[1] * 0.3
                ceil_y = alt * py / z + player_pos[0] * 0.3

                #ceil pos and color
                ceil_pos = int(ceil_x * SCALE % tex_size[0]), int(ceil_y * SCALE % tex_size[1])
                ceil_col = ceil_array[ceil_pos]

                #shading
                attenuation = min(max(1.5 * (abs(z) / HALF_HEIGHT), 0), 1)
                floor_col = floor_col[0] * attenuation, floor_col[1] * attenuation, floor_col[2] * attenuation



                #Fill screen

                screen_array[i,j] = floor_col
                screen_array[i, -j] = ceil_col

                new_alt +=alt


        return screen_array
    def draw(self):
        pg.surfarray.blit_array(self.app.screen, self.screen_array)

    def movement(self):
        sin_a = np.sin(self.angle)
        cos_a = np.cos(self.angle)
        dx = 0
        dy = 0
        speed_sin = SPEED * sin_a
        speed_cos = SPEED * cos_a

        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            dx += speed_cos
            dy += speed_sin
        if keys[pg.K_s]:
            dx += -speed_cos
            dy += -speed_sin
        if keys[pg.K_a]:
            dx += speed_sin
            dy += -speed_cos
        if keys[pg.K_d]:
            dx += -speed_sin
            dy += speed_cos
        self.pos[0] += dx
        self.pos[1] += dy

        if keys[pg.K_LEFT]:
            self.angle -= SPEED
        if keys[pg.K_RIGHT]:
            self.angle += SPEED

        if keys[pg.K_q]:
            self.alt += SPEED
        if keys[pg.K_e]:
            self.alt -= SPEED
        self.alt = min(max(self.alt, 0.3), 4.0)





