import pygame as pg
from sys import exit
import os 
import numpy as np
from random import randrange
from rede_neural import *

ALTURA = 768
LARGURA = 432

class Jogo:
    def __init__(self):
        pg.init()
        self.tela = pg.display.set_mode((LARGURA,ALTURA))
        self.relogio = pg.time.Clock()
        self.pos_chao = 0
        self.pos_chao2 = 504        
        self.vel_chao = 2.8
        self.fonte = os.path.join(os.getcwd(),"arquivos", "flappybird.ttf")  
        self.carregar_arquivos()
        self.num_vivos = 0
        self.ia_jogando = False

    def carregar_arquivos(self):

        self.spritesheet = pg.image.load(os.path.join(os.getcwd(),"arquivos", "spritesheet.png")).convert_alpha()
        self.fundo = self.spritesheet.subsurface((0,0),(LARGURA,ALTURA))
        self.chao = self.spritesheet.subsurface((876,0),(504,168))

    def update_tela(self):
        global pontos
        self.relogio.tick(60)
        self.tela.blit(self.fundo,(0,0))

        vivo = False
        for passaro in grp_passaros:
            if passaro.vivo: vivo = True
        if vivo:
            grp_canos.update()
        grp_canos.draw(jogo.tela)  

        grp_passaros.update()
        grp_passaros.draw(jogo.tela) 

        self.blit_chao()   

        self.mostrar_texto(f'{pontos}',80,(84,56,71,),LARGURA/2,40)     
        if self.ia_jogando:
            self.mostrar_texto(f'{self.num_vivos}',50,(84,56,71,),LARGURA-40,ALTURA-20)     

        for passaro in grp_passaros:            
            proximo_cano = 1000
            for i,cano in enumerate(grp_canos):
                if cano.x < proximo_cano and cano.x + 40 > passaro.x:
                    proximo_cano = cano.x
                    passaro.dist_x = cano.x - passaro.x
                    passaro.dist_y = cano.y - passaro.y
                    passaro.pesos = np.array([passaro.bias, passaro.dist_x/100, passaro.dist_y/100])

        pg.display.update()

    def blit_chao(self):
        y = ALTURA-150
        largura = 504

        if self.pos_chao < -largura:
            self.pos_chao = self.pos_chao2+largura
        elif self.pos_chao2 < -largura:
            self.pos_chao2 = self.pos_chao+largura

        vivo = False
        for passaro in grp_passaros:
            if passaro.vivo: vivo = True
        if vivo:
            self.pos_chao -= self.vel_chao
            self.pos_chao2 -= self.vel_chao

        
        self.tela.blit(self.chao,(self.pos_chao,y))
        self.tela.blit(self.chao,(self.pos_chao2,y))

    def mostrar_texto(self,texto,tamanho,cor,x,y):
        fonte = pg.font.Font(self.fonte, tamanho)
        texto = fonte.render(texto, False, cor)
        texto_rect = texto.get_rect()
        texto_rect.center = (x,y)
        self.tela.blit(texto, texto_rect)

    def eventos(self):
        global mortos
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                for passaro in grp_passaros:
                    passaro.pular()
                return
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    for passaro in grp_passaros:
                        passaro.pular()
                    return
            elif mortos:
                    global pontos
                    pontos = 0
                    return 'break'

class Passaro(pg.sprite.Sprite):
    def __init__(self,x,i):
        pg.sprite.Sprite.__init__(self)
        self.index = 0
        self.y = 300
        self.x = x
        self.num = i
        self.altura = self.y
        self.images = [jogo.spritesheet.subsurface((9,1473),(51,36)),
                        jogo.spritesheet.subsurface((93,1473),(51,36)),
                        jogo.spritesheet.subsurface((177,1473),(51,36)),
        ]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)
        self.rect.center = (self.x,self.y)
        self.vivo = True
        self.contador = 0
        self.tempo = 0
        self.angulo = 0
        self.fitness = 0
        self.last_pulo = 0
        self.bias = 1
        self.dist_x = 0
        self.dist_y = 0
        self.pesos = np.array([self.bias, self.dist_x/100, self.dist_y/100])
        
        self.passou = False

    def __repr__(self):
        return f'passaro_{self.num}'

    def update(self):
        vivo = False
        if self.y > ALTURA-168: 
            self.vivo = False
            self.y = ALTURA-168
            for passaro in grp_passaros:
                if passaro.vivo: vivo = True
            if vivo: self.x -= 2.8
            if self.x < -50:
                x = -100
        if self.y < -30:
            self.vivo = False
        if self.contador % 6 == 0:
            self.index += 1
            if self.index > 2: self.index = 0
        if self.angulo < -70: self.index = 1
        self.mover()
        self.image = pg.transform.rotate(self.images[self.index], self.angulo)   
        self.mask = pg.mask.from_surface(self.image)    
        self.rect.center = (self.x,self.y)

        self.contador += 1
        self.last_pulo += 1

        if self.vivo: self.fitness += 0.1

    def pular(self):
        if self.vivo and self.last_pulo > 5:
            self.tempo = 0
            self.altura = self.y
            self.index = 1
            self.last_pulo = 0

    def mover(self):
        self.velocidade_rotacao = 12
        self.velocidade = -4.2
        self.rotacao_max = 15
        limite_velocidade = 5
        self.tempo += 1
        deslocamento = 0.3*((self.tempo**2)/2) + self.velocidade * (self.tempo/2)
        
        if self.angulo < -70: limite_velocidade = 7
        if not self.vivo: 
            limite_velocidade = 9
            if deslocamento < 0:
                deslocamento = limite_velocidade

        if deslocamento > limite_velocidade: deslocamento = limite_velocidade
        elif deslocamento < 0: 
            deslocamento -= 0.9
        self.y += deslocamento

        if deslocamento < 0 or self.y < self.altura +36:
            if self.angulo < self.rotacao_max: 
                self.angulo += self.velocidade_rotacao
        elif self.angulo > -90: self.angulo -= self.velocidade_rotacao*0.8

class Canos(pg.sprite.Sprite):
    def __init__(self,x,i):
        pg.sprite.Sprite.__init__(self)
        self.image = jogo.spritesheet.subsurface((1458,436),(78,1100))
        self.y = randrange(180,ALTURA-300)
        self.x = x
        self.num = i
        self.rect = self.image.get_rect()
        self.rect.center = (self.x,self.y)
        self.mask = pg.mask.from_surface(self.image)
        self.passou = False
    
    def update(self):
        global pontos
        self.x -= 2.8
        if self.x < -80: 
            self.x += LARGURA+128
            self.passou = False
            self.y = randrange(180,ALTURA-300)
        
            for passaro in grp_passaros:
                passaro.passou = False

        self.rect.center = (self.x,self.y)
        
        for i,passaro in enumerate(grp_passaros):
            if self.x < passaro.x and not self.passou and passaro.vivo:
                pontos += 1
                self.passou = True
            if not passaro.passou and self.passou:
                if passaro.vivo: passaro.fitness += 30
                passaro.passou = True

    def __repr__(self):
        return f'cano_{self.num}'

jogo = Jogo()
grp_canos = pg.sprite.Group()
grp_passaros = pg.sprite.Group()
pontos = 0
mortos = True

def jogador():
    global passaro, mortos
    passaro = Passaro(LARGURA/2 - 75,1)
    grp_passaros.add(passaro)

    cano = Canos(LARGURA+300,1)
    grp_canos.add(cano)
    cano = Canos(LARGURA+580,2)
    grp_canos.add(cano)
    while True:
        jogo.update_tela()
        jogo.eventos()
        mortos = True
        for passaro in grp_passaros:
            if pg.sprite.spritecollide(passaro,grp_canos,False,pg.sprite.collide_mask):                
                passaro.vivo = False
            if passaro.vivo or passaro.y < ALTURA-168:
                mortos = False
            passaro.fitness = round(passaro.fitness,2)
        if mortos:    
            while True:
                if jogo.eventos() == 'break': 
                    grp_passaros.empty()
                    grp_canos.empty()
                    passaro = Passaro(LARGURA/2 - 75,1)
                    grp_passaros.add(passaro)
                    cano = Canos(LARGURA+300,1)
                    grp_canos.add(cano)
                    cano = Canos(LARGURA+580,2)
                    grp_canos.add(cano)
                    break

def ia_jogando():
    z = 1
    redes = []
    cano = Canos(LARGURA+300,1)
    grp_canos.add(cano)
    cano = Canos(LARGURA+580,2)
    grp_canos.add(cano)
    jogo.ia_jogando = True

    for i in range(100):
        passaro = Passaro(LARGURA/2 - 75,z)
        grp_passaros.add(passaro)
        rede = Rede(z)
        redes.append(rede)
        z+=1
    pesos = [0,0]
    melhor = [0,0]
    global pontos
    while True:
        jogo.update_tela()
        for event in pg.event.get():
                    if event.type == pg.QUIT:
                        print(pesos)
                        pg.quit()
                        exit()
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_SPACE: pass

        for i, passaro in enumerate(grp_passaros):
            valor = calcular_jogada(passaro,redes[i])
            if valor >= 0.5:
                passaro.pular()

        mortos = True
        jogo.num_vivos = 0
        for passaro in grp_passaros:
            if pg.sprite.spritecollide(passaro,grp_canos,False,pg.sprite.collide_mask):                
                passaro.vivo = False
            if passaro.vivo or passaro.y < ALTURA-168:    
                mortos = False
            if passaro.vivo: jogo.num_vivos += 1
            passaro.fitness = round(passaro.fitness,2)
            
        if mortos:
            for i,passaro in enumerate(grp_passaros):
                redes[i].fitness = passaro.fitness
                if redes[i].fitness > redes[i].best_fitness:
                    redes[i].best_fitness = redes[i].fitness
                if passaro.fitness > melhor[1]:
                    melhor = [redes[i], passaro.fitness, pontos]
                    pesos = [redes[i],redes[i].pesos]

            print(melhor, f'geracao: {(z+97)//100}', f'/ pontuação max da gen: {pontos}')
            redes,z = evoluir(redes,z)
            acabou = True
            if acabou:                               
                pontos = 0
                grp_passaros.empty()
                grp_canos.empty()
                cano = Canos(LARGURA+300,1)
                grp_canos.add(cano)
                cano = Canos(LARGURA+580,2)
                grp_canos.add(cano)
                for i in range(100):
                    passaro = Passaro(LARGURA/2 - 75,z)
                    grp_passaros.add(passaro)
                
                acabou = False

player = False
if __name__ == '__main__':
    if player:
        jogador()
    else:
        ia_jogando()