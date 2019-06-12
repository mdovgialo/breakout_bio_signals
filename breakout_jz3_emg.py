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
from typing import List, Any

# import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from obci_cpp_amplifiers.amplifiers import TmsiCppAmplifier


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

    def kalibracja(self):
        BUF_LEN = 32
        KAL_LEN = 5

        self.screen.fill(self.bgcolour)
        text = pygame.font.Font(None, 40).render('Część I: Rozluźnij mięsień', True, (0, 255, 255), self.bgcolour)
        textrect = text.get_rect()
        textrect.center = (self.width / 2, self.height / 2)
        self.screen.blit(text, textrect)
        pygame.draw.arc(self.screen, (0, 255, 255),
                        ((self.width / 2 - 25, self.height / 2 + 50),
                         (50, 50)), np.pi / 2, np.pi / 2, 10)
        pygame.display.flip()


        clock = pygame.time.Clock()
        clock.tick(60)# 60 frames per second
        t0_0 = t0=t = pygame.time.get_ticks() / 1000
       # t0_0 = t0
        #t = t0
        std_luz: List[Any] = []
        std_nap: List[Any] = []
        i=0
        while (t - t0_0 < KAL_LEN):
            ####
            # tu odbieram bufory i zbieram statystyki luźnego mięśnia
            packet = amp.get_samples(BUF_LEN)
            X = samples_to_microvolts(packet.samples)
            x = X[:, 0] - X[:, 1]
            syg = x - np.mean(x)
            #print(t - t0_0 , np.std(syg))
            std_luz.append(np.std(syg))

            ####
            t = pygame.time.get_ticks() / 1000  #
            if (t - t0) > 1:
                self.screen.fill(self.bgcolour)
                self.screen.blit(text, textrect)
                pygame.draw.arc(self.screen, (0, 255, 255),
                                ((self.width / 2 - 25, self.height / 2 + 50),
                                 (50, 50)), np.pi / 2, np.pi / 2 - np.pi * 2 / KAL_LEN * (t - t0_0), 10)
                #print(t)
                t0 = t
                pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()


        text = pygame.font.Font(None, 40).render('Część II: Napnij mięsień', True, (214, 21, 21), self.bgcolour)
        textrect = text.get_rect()
        textrect.center = (self.width / 2, self.height / 2)
        t0_1 =t0 =t  = pygame.time.get_ticks() / 1000
        self.screen.fill(self.bgcolour)
        self.screen.blit(text, textrect)
        pygame.draw.arc(self.screen, (214, 21, 21),
                                      ((self.width / 2 - 25, self.height / 2 + 50),
                                       (50, 50)), np.pi / 2, np.pi / 2 , 10)

        pygame.display.flip()

        while (t - t0_1 < KAL_LEN):
            clock.tick(60)# 60 frames per second
            ####
            # tu odbieram bufory i zbieram statystyki napiętego mięśnia
            packet = amp.get_samples(BUF_LEN)
            X = samples_to_microvolts(packet.samples)
            x = X[:, 0] - X[:, 1]
            syg = x - np.mean(x)
            #print(t - t0_1 , np.std(syg))
            std_nap.append(np.std(syg))

            ####

            t = pygame.time.get_ticks() / 1000  #
            if (t - t0) > 1:
                self.screen.fill(self.bgcolour)
                self.screen.blit(text, textrect)
                pygame.draw.arc(self.screen, (214, 21, 21),
                                ((self.width / 2 - 25, self.height / 2 + 50),
                                 (50, 50)), np.pi / 2, np.pi / 2 - np.pi * 2 / KAL_LEN * (t - t0_1), 10)
                #print(t)
                t0 = t
                pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
        return std_luz, std_nap

    def main(self,std_luz, std_nap):
        alfa = 0.03 # szybkość zmiany położenia
        xspeed_init = 3
        yspeed_init = 3
        max_lives = 5
        score = 0
        BUF_LEN = 32
        M_nap = np.median(std_nap)
        M_luz = np.median(std_luz)
        sd = M_nap - M_luz

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
            packet = amp.get_samples(BUF_LEN)
            X = samples_to_microvolts(packet.samples)
            # if i == 0:
            #     t0 = packet.ts[0]
            #     # t00 = t0
            #     i += 1
            # dt = packet.ts[0] - t0
            # t0 = packet.ts[0]
            x = X[:, 0] - X[:, 1]
            syg = x - np.mean(x)
            std = np.std(syg)
            ################
            # normalizujemy
            mx_new = (std -np.mean((M_nap, M_luz)) )/sd
            mx = (1-alfa)*mx+ alfa*mx_new
            if mx<0:
                mx=0
            elif mx>1:
                mx=1


            # przesuwamy paletkę
            batrect.centerx = mx*self.width
            #print(t, std)
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


class Wall():

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


if __name__ == '__main__':
    amps = TmsiCppAmplifier.get_available_amplifiers('usb')
    amp = TmsiCppAmplifier(amps[0])

    amp.sampling_rate = 512

    amp.start_sampling()
    gains = np.array(amp.current_description.channel_gains)
    offsets = np.array(amp.current_description.channel_offsets)

    br = Breakout()
    std_luz, std_nap = br.kalibracja()
    # plt.subplot(2,1,1)
    # plt.hist(std_luz)
    # plt.subplot(2,1,2)
    # plt.hist(std_nap)
    # plt.show()
    # print('*******************')
    # print('luz')
    # print(std_luz)
    # print('nap')
    # print(std_nap)
    # print('*******************')
    br.main(std_luz, std_nap)
