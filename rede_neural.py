
from random import randint,random, uniform,choice
import numpy as np

def tangente_hiperbolica(x):
    return (np.exp(x) - np.exp(-x)) / (np.exp(x) + np.exp(-x))

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

class Rede:
    def __init__(self,i):
        self.num = i
        self.n_1_1 = np.array([uniform(-1,1) for i in range(3)])
        self.n_1_2 = np.array([uniform(-1,1) for i in range(3)])
        self.n_2_1 = np.array([uniform(-1,1) for i in range(2)])
        self.n_2_2 = np.array([uniform(-1,1) for i in range(2)])
        self.n_final = np.array([uniform(-1,1) for i in range(2)])

        self.pesos = [self.n_1_1,self.n_1_2,self.n_2_1,self.n_2_2,self.n_final]
        self.genoma = self.pesos

        self.fitness = 0
        self.best_fitness = 0


    def __repr__(self):
        return f'rede_{self.num}'

class RedeEvolve:
    def __init__(self,i,pesos):
        self.num = i
        self.n_1_1 = np.array(pesos[0:3])
        self.n_1_2 = np.array(pesos[3:6])
        self.n_2_1 = np.array(pesos[6:8])
        self.n_2_2 = np.array(pesos[8:10])
        self.n_final = np.array(pesos[10:12])

        self.pesos = [self.n_1_1,self.n_1_2,self.n_2_1,self.n_2_2,self.n_final]
        self.genoma = self.pesos

        self.fitness = 0
        self.best_fitness = 0

    def __repr__(self):
        return f'rede_{self.num}'


def calcular_jogada(passaro, rede):
    saida_n_1_1 = round(tangente_hiperbolica(np.sum(passaro.pesos * rede.n_1_1)),6)
    saida_n_1_2 = round(tangente_hiperbolica(np.sum(passaro.pesos * rede.n_1_2)),6)
    saidas_primeira_camada = np.array([saida_n_1_1,saida_n_1_2])
    saida_n_2_1 = round(tangente_hiperbolica(np.sum(saidas_primeira_camada * rede.n_2_1)),6)
    saida_n_2_2 = round(tangente_hiperbolica(np.sum(saidas_primeira_camada * rede.n_2_2)),6)
    saidas_segunda_camada = np.array([saida_n_2_1,saida_n_2_2])

    saida_final = round(sigmoid(np.sum(saidas_segunda_camada * rede.n_final)),6)
    
    return saida_final


def evoluir(redes,z):
    maior = 0
    maior2 = 0
    maior3 = 0
    melhor = 0
    melhor2 = 0
    melhor3 = 0

    evolved = []

    for i,rede in enumerate(redes):
        if rede.fitness > maior:
            maior = rede.fitness
            rede.fitness = 0
            melhor = i
        elif rede.fitness > maior2:
            maior2 = rede.fitness
            rede.fitness = 0
            melhor2 = i
        elif rede.fitness > maior3:
            maior3 = rede.fitness
            rede.fitness = 0
            melhor3 = i

    evolved.append(redes[melhor])
    evolved.append(redes[melhor2])
    evolved.append(redes[melhor3])

    melhor = redes[melhor]
    melhor2 = redes[melhor2]
    melhor3 = redes[melhor3]

    
    genoma = []
    for neuronio in melhor.pesos:
        for peso in neuronio:
            genoma.append(peso)
    melhor.genoma = genoma
    genoma = []
    for neuronio in melhor2.pesos:
        for peso in neuronio:
            genoma.append(peso)
    melhor2.genoma = genoma
    genoma = []
    for neuronio in melhor3.pesos:
        for peso in neuronio:
            genoma.append(peso)
    melhor3.genoma = genoma

    main_genomas = [melhor.genoma,melhor2.genoma,melhor3.genoma,[uniform(-1,1) for i in range(12)]]
    genomas = [melhor.genoma,melhor2.genoma,melhor3.genoma]

    for i in range(97):
        pai = choice(main_genomas)        
        mae = choice(genomas)


        if i%2 == 0:
            index = randint(0,11)
            j = randint(0,1)
            if j == 1:
                filho = pai[:index]+mae[index:]
            else:
                filho = mae[:index]+pai[index:]
        else:
            filho = []
            for j in range(12):
                quem = randint(0,1)
                if quem == 0:
                    filho.append(pai[j])
                else:
                    filho.append(mae[j])

            
        filho = mutate(filho)

        if i > 87: filho = mutate(melhor.genoma,True)
        
        genomas.append(filho)

        filho = RedeEvolve(z,filho)
        z += 1
        evolved.append(filho)
   
    return evolved , z

def mutate(individuo,pai=False):

    a = randint(1,10)
    if pai: a = randint(1,7)
    if a <= 1:
        index = randint(0,11)
        individuo[index] = uniform(-1,1)

    if a <= 7:
        b = random()
        for i in range(a):
            index = randint(0,11)
            individuo[index] *= b

    return individuo