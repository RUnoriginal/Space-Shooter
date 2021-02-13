# coding: utf-8
#import des bibliothèques
import pygame
import os
import random
import time
from pygame.locals import*

#initialisation
pygame.init()

#affichage du titre
pygame.display.set_caption("Space Shooter")

#création de la fenêtre
width, height= 500, 500
window=pygame.display.set_mode((width,height))

#import des images
player=pygame.image.load("assets/joueur.png")
shuttle=pygame.image.load("assets/soucoupe.png")
spearhead=pygame.image.load("assets/fleche.png")
moon=pygame.image.load("assets/demilune.png")
player_shot=pygame.image.load("assets/tir_joueur.png")
shuttle_shot=pygame.image.load("assets/tir_soucoupe.png")
spearhead_shot=pygame.image.load("assets/tir_fleche.png")
moon_shot=pygame.image.load("assets/tir_demilune.png")

#import du fond
background=pygame.image.load("assets/fond_espace.png")

class Laser:
    def __init__(self, x, y, img):
        self.x=x
        self.y=y
        self.img=img
        self.mask=pygame.mask.from_surface(self.img)

    def render(self, fen):                                 #affichage de l'objet
        window.blit(self.img, (self.x, self.y))

    def move(self, speed):                            #définition du mouvement
        self.y+=speed

    def screen_exit(self, y):                               #permet de supprimer le laser après la sortie de l'écran
        return not self.y<=height and self.x>=0

    def collision(self, obj):                                 #renvoie les informations utiles à la simulation de la collision
        return contact(obj, self)

class Ship:                            #création du type d'objet "Ship", pour le joueur ou les ennemis
    def __init__(self, x, y, health=100):
        self.x=x                                    #position de l'objet
        self.y=y
        self.health= health                           #santé définie de l'objet
        self.ship_img=None                     #classe générale, on ne doit pas afficher d'image, pour permettre d'afficher les images de chaque vaisseau spécifiquement
        self.laser_img=None
        self.lasers=[]                          #inclut tous les objets de type laser dans la liste

    def render(self,fen):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.render(window)

    def move_laser(self, speed, obj):
        for laser in self.lasers:
            laser.move(speed)
            if laser.screen_exit(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health-=10
                self.lasers.remove(laser)

    def shoot(self):
            laser=Laser(self.x+15,self.y, self.laser_img)
            self.lasers.append(laser)

class Player(Ship):                                 #création de l'objet Player de type Ship
    def __init__(self, x, y, health=100):
        super().__init__(x,y,health)                        #utilisation des variables définies dans Ship
        self.ship_img=player
        self.laser_img=player_shot
        self.mask=pygame.mask.from_surface(self.ship_img)   #permet une collision au pixel près: la collision se fera sur un pixel visible, pas sur un carré autour de l'image
        self.health_max= health

    def move_laser(self, speed, objs):
        for laser in self.lasers:
            laser.move(speed)
            if laser.screen_exit(0):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def render(self,window):
        super().render(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y+42, 32, 5))
        pygame.draw.rect(window, (0,50,255), (self.x, self.y+42, 32*(self.health/self.health_max), 5))

class Ennemy(Ship):
    COLOR_DICT={                                              #création d'une liste contenant les images des vaisseaux en fonction de la couleur, pour permettre des apparitions à partir de ces couleurs
                "orange":(spearhead, spearhead_shot),
                "green":(shuttle, shuttle_shot),
                "blue":(moon, moon_shot)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img=self.COLOR_DICT[color] #Les images correspondent aux images du COLOR_DICT
        self.mask=pygame.mask.from_surface(self.ship_img)

    def move(self, speed):
        self.y+=speed

    def shoot(self):
        laser=Laser(self.x+15,self.y+32, self.laser_img)
        self.lasers.append(laser)

def contact(obj1, obj2):
    distance_x=obj2.x-obj1.x
    distance_y=obj2.y-obj1.y
    return obj1.mask.overlap(obj2.mask, (distance_x, distance_y)) != None #montre la collision entre les masques, seulement si les hitboxes sont en contact.

def main():
    over=False
    FPS=60            #images par seconde
    level=0
    lives=5
    font=pygame.font.SysFont("comicsans",35)
    defeat_font=pygame.font.SysFont("comicsans",60)

    ennemies=[]
    wave_length=4
    speed_ennemy=1

    speed_player=5

    speed_laser=6

    player=Player(234, 430)

    time=pygame.time.Clock()

    countdown_defeat=0

    def global_rendering():               #gestion des images
        window.blit(background,(0,0))                #affichage de l'image de fond
        #affichage du texte
        lives1=font.render("Lives: "+str(lives), True,(255,255,255))
        level1=font.render("Level: "+str(level), True, (255, 255, 255))
        window.blit(lives1, (10,10))
        window.blit(level1, (375,10))

        for ennemy in ennemies:
            ennemy.render(window)

        player.render(window)

        if over==True:
            over1=defeat_font.render("You lost!!", 1, (255,255,255))
            window.blit(over1, (width/2-over1.get_width()/2, 250))
            pygame.quit()
            quit()

        pygame.display.update()                    #actualisation de l'écran

    while over==False:
        time.tick(FPS)                         #la boucle s'active 60 fois par seconde

        if lives<=0 or player.health<=0:
            over=True

        if len(ennemies)==0:
            level+=1
            wave_length+=2
            for i in range(wave_length):
                ennemy=Ennemy(random.randrange(40, width-40), random.randrange(-500, -100), random.choice(["orange", "green","blue"]))
                ennemies.append(ennemy)

        for event in pygame.event.get():
            if event.type==QUIT:         #gestion de la fermeture de la fenêtre
                over=True
                pygame.quit()
                quit()

        keys= pygame.key.get_pressed()          #gestion des mouvements du joueur, des projectiles et des bords de l'écran
        if keys[pygame.K_LEFT] and player.x-speed_player>0:
            player.x-=speed_player
        if keys[pygame.K_RIGHT] and player.x+speed_player+32<width:
            player.x+=speed_player
        if keys[pygame.K_UP] and player.y-speed_player>0:
            player.y-=speed_player
        if keys[pygame.K_DOWN] and player.y+speed_player+42<height:
            player.y+=speed_player
        if keys[pygame.K_SPACE]:
            player.shoot()

        for ennemy in ennemies[:]:
            ennemy.move(speed_ennemy)
            ennemy.move_laser(speed_laser, player)

            if random.randrange(0,120)==1:
                ennemy.shoot()

            if contact(ennemy, player):
                player.health-=10
                ennemies.remove(ennemy)

            elif ennemy.y+32>height:
                lives-=1
                ennemies.remove(ennemy)

        player.move_laser(-speed_laser, ennemies)

        global_rendering()
main()