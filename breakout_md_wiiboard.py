#!/usr/bin/env python

#
#   Breakout V 0.1 June 2009
#
#   Copyright (C) 2009 John Cheetham    
#
#   web   : http://www.johncheetham.com/projects/breakout
#   email : developer@johncheetham.com
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#    
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import pygame
import random
import sys
import math
from typing import List, Any

# import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from obci_wiiboard.drivers.core import get_wiiboard_devices, get_wiiboard_device
from threading import Thread, Lock
from queue import Queue, Empty

def samples_to_microvolts(samples):  # z jednostek wzmacniacza do mikrowoltów
    return samples * gains + offsets


class Breakout():
    def __init__(self):
        pygame.init()
        self.bgcolour = 0x2F, 0x4F, 0x4F  # darkslategrey        
        size = self.width, self.height = 640, 480
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        #self.screen = pygame.display.set_mode(size)

        self.screen.fill(self.bgcolour)
        self.creen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        self.screen.fill(self.bgcolour)
        pygame.display.flip()
        pong = pygame.mixer.Sound('Blip_1-Surround-147.wav')
        pong.set_volume(10)
        pong.play(0)
        pygame.time.wait(500)

    def main(self, wiiboard_state_thread):
        alfa = 0.03 # szybkość zmiany położenia
        xspeed_init = 3
        yspeed_init = 3
        max_lives = 5
        score = 0
        BUF_LEN = 32

        bat = pygame.image.load("bat.png").convert()
        batrect = bat.get_rect()

        ball = pygame.image.load("ball.png").convert()
        ball.set_colorkey((255, 255, 255))
        ballrect = ball.get_rect()

        pong = pygame.mixer.Sound('Blip_1-Surround-147.wav')
        pong.set_volume(10)
        pong.play(0)
        wall = Wall()
        wall.build_wall(self.width)

        # Initialise ready for game loop
        batrect = batrect.move((self.width / 2) - (batrect.right / 2), self.height - 20)
        ballrect = ballrect.move(self.width / 2, self.height / 2)
        xspeed = xspeed_init
        yspeed = yspeed_init
        lives = max_lives
        clock = pygame.time.Clock()
        pygame.key.set_repeat(1, 30)
        pygame.mouse.set_visible(0)  # turn off mouse pointer
        i = 0
        mx = 0.5
        while 1:

            # 60 frames per second
            clock.tick(64)

            # process key presses
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
            t = pygame.time.get_ticks() / 1000  # to powinien być czas w sek.
            ##############
            ### TU odczytywanie bufora danych i jego analiza
            sample = wiiboard_state_thread.latest_sample
            ################

            try:
               mx_new = wiiboard_to_position(sample) / 2.0 + 0.5
            except ZeroDivisionError:
                mx_new = 0.5
            if math.isnan(mx_new):
                mx_new = 0.5
#            mx = (1-alfa)*mx+ alfa*mx_new
            mx = mx_new
            if mx<0:
                mx=0
            elif mx>1:
                mx=1

            if (sample.top_left + sample.top_right + sample.bottom_left + sample.bottom_right) < 200:
                continue

            # przesuwamy paletkę
            batrect.centerx = mx*self.width

            if (batrect.left < 0):
                batrect.left = 0
            if (batrect.right > self.width):
                batrect.right = self.width

            # check if bat has hit ball    
            if ballrect.bottom >= batrect.top and \
                    ballrect.bottom <= batrect.bottom and \
                    ballrect.right >= batrect.left and \
                    ballrect.left <= batrect.right:
                yspeed = -yspeed
                pong.play(0)
                offset = ballrect.center[0] - batrect.center[0]
                # offset > 0 means ball has hit RHS of bat                   
                # vary angle of ball depending on where ball hits bat                      
                if offset > 0:
                    if offset > 30:
                        xspeed = 7
                    elif offset > 23:
                        xspeed = 6
                    elif offset > 17:
                        xspeed = 5
                else:
                    if offset < -30:
                        xspeed = -7
                    elif offset < -23:
                        xspeed = -6
                    elif offset < -17:
                        xspeed = -5

                        # move bat/ball
            ballrect = ballrect.move(xspeed, yspeed)
            if ballrect.left < 0 or ballrect.right > self.width:
                xspeed = -xspeed
                pong.play(0)
            if ballrect.top < 0:
                yspeed = -yspeed
                pong.play(0)

                # check if ball has gone past bat - lose a life
            if ballrect.top > self.height:
                lives -= 1
                # start a new ball
                xspeed = xspeed_init
                if random.random() > 0.5:
                    xspeed = -xspeed
                yspeed = yspeed_init
                ballrect.center = self.width * random.random(), self.height / 3
                if lives == 0:
                    msg = pygame.font.Font(None, 70).render("Game Over", True, (0, 255, 255), self.bgcolour)
                    msgrect = msg.get_rect()
                    msgrect = msgrect.move(self.width / 2 - (msgrect.center[0]), self.height / 3)
                    self.screen.blit(msg, msgrect)
                    pygame.display.flip()
                    # process key presses
                    #     - ESC to quit
                    #     - any other key to restart game
                    while 1:
                        restart = False
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                    sys.exit()
                                if not (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT):
                                    restart = True
                        if restart:
                            self.screen.fill(self.bgcolour)
                            wall.build_wall(self.width)
                            lives = max_lives
                            score = 0
                            break

            if xspeed < 0 and ballrect.left < 0:
                xspeed = -xspeed
                pong.play(0)

            if xspeed > 0 and ballrect.right > self.width:
                xspeed = -xspeed
                pong.play(0)

            # check if ball has hit wall
            # if yes yhen delete brick and change ball direction
            index = ballrect.collidelist(wall.brickrect)
            if index != -1:
                if ballrect.center[0] > wall.brickrect[index].right or \
                        ballrect.center[0] < wall.brickrect[index].left:
                    xspeed = -xspeed
                else:
                    yspeed = -yspeed
                pong.play(0)
                wall.brickrect[index:index + 1] = []
                score += 10

            self.screen.fill(self.bgcolour)
            scoretext = pygame.font.Font(None, 40).render(str(score), True, (0, 255, 255), self.bgcolour)
            scoretextrect = scoretext.get_rect()
            scoretextrect = scoretextrect.move(self.width - scoretextrect.right, 0)
            self.screen.blit(scoretext, scoretextrect)

            for i in range(0, len(wall.brickrect)):
                self.screen.blit(wall.brick, wall.brickrect[i])

                # if wall completely gone then rebuild it
            if wall.brickrect == []:
                wall.build_wall(self.width)
                xspeed = xspeed_init
                yspeed = yspeed_init+2
                ballrect.center = self.width / 2, self.height / 3

            self.screen.blit(ball, ballrect)
            self.screen.blit(bat, batrect)
            pygame.display.flip()


class Wall:
    def __init__(self):
        self.brick = pygame.image.load("brick.png").convert()
        brickrect = self.brick.get_rect()
        self.bricklength = brickrect.right - brickrect.left
        self.brickheight = brickrect.bottom - brickrect.top

    def build_wall(self, width):
        xpos = 0
        ypos = 60
        adj = 0
        self.brickrect = []
        for i in range(0, 52):
            if xpos > width:
                if adj == 0:
                    adj = self.bricklength / 2
                else:
                    adj = 0
                xpos = -adj
                ypos += self.brickheight

            self.brickrect.append(self.brick.get_rect())
            self.brickrect[i] = self.brickrect[i].move(xpos, ypos)
            xpos = xpos + self.bricklength

class Sample:
    def __init__(self):
        self.top_left = 0
        self.top_right = 0
        self.bottom_left = 0
        self.bottom_right = 0


class WiiboardStateThread(Thread):
    def __init__(self, *args, **kwargs):
        self._latest_sample = Sample()
        self._lock = Lock()
        super().__init__(*args, **kwargs)

    def run(self):
        wiiboards = get_wiiboard_devices()
        non_dummy = [i for i in wiiboards.keys() if i != 'dummy']
        wiiboard = get_wiiboard_device(non_dummy[0])
        while True:
            sample = wiiboard.sample()
            with self._lock:
                self._latest_sample = sample

    @property
    def latest_sample(self):
        with self._lock:
            return self._latest_sample



def wiiboard_to_position(sample):
    """Sample zawiera 4 zmienne:
    sample.top_left
    sample.top_right
    sample.bottom_left
    sample.bottom_right
    zawierające nacisk na czujniki wiiboarda w rogach: lewym górnym, prawym górnym, lewym dolnym i prawym dolnym
    w dekagramach. (1 kilogram = 100 dekagramów).

    Gra oczekuje pozycję palety od -1 (najbardziej w lewo) do 1 (najbardziej w prawo) i 0 - centrum

    """

    #####################################
    top_l = np.array([-1, 1])
    top_r = np.array([1, 1])
    bot_l = np.array([-1, -1])
    bot_r = np.array([1, -1])

    xy = ((top_l * sample.top_left
           + top_r * sample.top_right
           + bot_l * sample.bottom_left
           + bot_r * sample.bottom_right)
          / (sample.top_left + sample.top_right + sample.bottom_left + sample.bottom_right))
    x = xy[0]
    ######################################

    return x * 1.5


if __name__ == '__main__':
    q = Queue()
    thread = WiiboardStateThread()
    thread.daemon = True
    thread.start()

    br = Breakout()
    br.main(thread)
