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

    def update(self):
        #Player movement
        time = self.app.time
        pos = np.array([time, 0])



        self.screen_array = self.render_frame(self.floor_array, self.ceil_array, self.screen_array, self.tex_size, pos)

    @staticmethod
    @njit(fastmath = True, parallel = True)
    def render_frame(floor_array, ceil_array, screen_array, tex_size, pos):
        #Iterates through the entire screen array
        for i in prange(WIDTH):
            for j in range(HALF_HEIGHT, HEIGHT):
                x = HALF_WIDTH - i
                y = j + FOCAL_LEN
                z = j - HALF_HEIGHT + 0.01

                # Projection
                px = (x / z + pos[1]) * SCALE
                py = (y / z + pos[0]) * SCALE

                #Floor pos and color
                floor_pos = int(px % tex_size[0]), int(py % tex_size[1])
                floor_col = floor_array[floor_pos]

                #Ceiling pos and color
                ceil_pos = floor_pos
                ceil_col = ceil_array[ceil_pos]

                #shading
                attenuation = min(max(1.5 * (abs(z) / HALF_HEIGHT), 0), 1)
                floor_col = floor_col[0] * attenuation, floor_col[1] * attenuation, floor_col[2] * attenuation

                #Ceiling
                ceil_col = (ceil_col[0] * attenuation, ceil_col[1] * attenuation, ceil_col[2] * attenuation)


                #Fill screen

                screen_array[i,j] = floor_col
                screen_array[i, -j] = ceil_col


        return screen_array
    def draw(self):
        pg.surfarray.blit_array(self.app.screen, self.screen_array)
