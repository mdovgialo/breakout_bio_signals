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

import sys, pygame, random
import numpy as np

class Breakout():
    def __init__(self):
        pygame.init()  
        self.bgcolour = 0x2F, 0x4F, 0x4F  # darkslategrey        
        size = self.width, self.height = 640, 480          
        self.screen = pygame.display.set_mode(size)
        self.screen.fill(self.bgcolour)
        #screen = pygame.display.set_mode(size, pygame.FULLSCREEN)    
    
    def kalibracja(self):
        text = pygame.font.Font(None,40).render('Część I: Rozluźnij mięsień', True, (0,255,255), self.bgcolour)
        textrect = text.get_rect()
        textrect.center = (self.width/2,self.height/2) # = scoretextrect.move(self.width - scoretextrect.right, 0)
        self.screen.blit(text, textrect)
         
        pygame.display.flip()
        clock = pygame.time.Clock()
        t0 = pygame.time.get_ticks()/1000 
        t0_0= t0
        t = t0
        while(t-t0_0<15):
    #        # 60 frames per second
           clock.tick(60)
           
           t = pygame.time.get_ticks()/1000 #
           if (t-t0)>1:
               self.screen.fill(self.bgcolour)
               self.screen.blit(text, textrect)
               pygame.draw.arc(self.screen, (10, 200, 100),
                               ((self.width/2-25,self.height/2+50), 
                                (50,50)), np.pi/2, np.pi/2-np.pi*2/15*(t-t0_0), 10)
               print(t)
               t0=t
                ####
                # tu odbieram bufory i zbieram statystyki napiętego mięśnia
                ####
               pygame.display.flip()
               
           for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
        
        text = pygame.font.Font(None,40).render('Część II: Napnij mięsień', True, (0,255,255), self.bgcolour)
        textrect = text.get_rect()
        textrect.center = (self.width/2,self.height/2) # = scoretextrect.move(self.width - scoretextrect.right, 0)
        self.screen.blit(text, textrect)
         
        pygame.display.flip()
        
        t0_1 = pygame.time.get_ticks()/1000 
        t = t0_1
        t0 = t0_1
        while(t-t0_1<15):
    #        # 60 frames per second
           clock.tick(60)
           
           t = pygame.time.get_ticks()/1000 #
           if (t-t0)>1:
               self.screen.fill(self.bgcolour)
               self.screen.blit(text, textrect)
               pygame.draw.arc(self.screen, (0, 200, 100),
                               ((self.width/2-25,self.height/2+50), 
                                (50,50)), np.pi/2, np.pi/2-np.pi*2/15*(t-t0_1), 10)
               print(t)
               t0=t
                ####
                # tu odbieram bufory i zbieram statystyki napiętego mięśnia
                ####
               pygame.display.flip()
               
           for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                        
    def main(self):
          
        xspeed_init = 10
        yspeed_init = 10
        max_lives = 5
        bat_speed = 30
        score = 0 
        

        

        bat = pygame.image.load("bat.png").convert()
        batrect = bat.get_rect()

        ball = pygame.image.load("ball.png").convert()
        ball.set_colorkey((255, 255, 255))
        ballrect = ball.get_rect()
       
        pong = pygame.mixer.Sound('Blip_1-Surround-147.wav')
        pong.set_volume(10)        
        
        wall = Wall()
        wall.build_wall(self.width)

        # Initialise ready for game loop
        batrect = batrect.move((self.width / 2) - (batrect.right / 2), self.height - 20)
        ballrect = ballrect.move(self.width / 2, self.height / 2)       
        xspeed = xspeed_init
        yspeed = yspeed_init
        lives = max_lives
        clock = pygame.time.Clock()
        pygame.key.set_repeat(1,30)       
        pygame.mouse.set_visible(0)       # turn off mouse pointer

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
            t = pygame.time.get_ticks()/1000 # to powinien być czas w sek.            
            x = int(np.sin(2*np.pi*0.2* t)*  self.width/2)+self.width/2   # położenie centrum paletki ma sie zminiac sinusoidalnie                         
            ##############3
            ### TU odczytywanie bufora danych i jego analiza
            ################
            batrect.centerx = ballrect.centerx#x # batrect.move(-bat_speed, 0)     
            #print(t,x)
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
                    elif xspeed < -17:
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
                #rand = random.random()                
                if random.random() > 0.5:
                    xspeed = -xspeed 
                yspeed = yspeed_init            
                ballrect.center = self.width * random.random(), self.height / 3                                
                if lives == 0:                    
                    msg = pygame.font.Font(None,70).render("Game Over", True, (0,255,255), self.bgcolour)
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
            scoretext = pygame.font.Font(None,40).render(str(score), True, (0,255,255), self.bgcolour)
            scoretextrect = scoretext.get_rect()
            scoretextrect = scoretextrect.move(self.width - scoretextrect.right, 0)
            self.screen.blit(scoretext, scoretextrect)

            for i in range(0, len(wall.brickrect)):
                self.screen.blit(wall.brick, wall.brickrect[i])    

            # if wall completely gone then rebuild it
            if wall.brickrect == []:              
                wall.build_wall(self.width)                
                xspeed = xspeed_init
                yspeed = yspeed_init                
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
        for i in range (0, 52):           
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
    br = Breakout()
    br.kalibracja()
    br.main()


