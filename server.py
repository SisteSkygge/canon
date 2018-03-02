#!/usr/bin/python3
# -*- coding:utf-8 -*-

import socket
from threading import Thread
import pickle

class Waiter(Thread):
    def __init__(self, socket, client_list, adress_list, listener_list, game_list):
        Thread.__init__(self)
        self.socket = socket
        self.client_connected = client_list
        self.adress_list = adress_list
        self.listener_list = listener_list
        self.game_list = game_list

    def run(self):
        while True:
            self.socket.listen(5)
            client, adress = self.socket.accept()
            self.client_connected.append(client)
            self.adress_list.append(adress)
            self.listener_list.append(Listener(client, adress, self, self.game_list))
            self.listener_list[len(listener_list)-1].start()
            print("Client connecte : {}, nombre d'adresse : {}, nombre de listeners : {}, nombres de game : {}".format(len(self.client_connected), len(self.adress_list), len(self.listener_list), len(self.game_list)))

    def client_disconnected(self, client):
        for i in range(len(self.client_connected)):
            if(self.client_connected[i]==client):
                del self.client_connected[i]
                del self.adress_list[i]
                del self.listener_list[i]
                break

class Listener(Thread):
    def __init__(self, client, adress, waiter, game_list):
        Thread.__init__(self)
        self.client = client
        self.adress = adress
        self.waiter = waiter
        self.game_list = game_list

    def run(self):
        active = True
        while active:
            try:
                #On lit le message
                self.msg = self.client.recv(1024)
                self.msg = pickle.loads(self.msg)
                print("{} : {}".format(self.adress, self.msg))
                if(self.msg=="Test"):
                    self.client.send(pickle.dumps("Ok"))
                if(self.msg=="Info session"):
                    print("Envoie des informations...")
                    self.give_info_session()
                if(self.msg=="New party"):
                    print("Création d'une nouvelle partie...")
                    self.create_new_game(self.adress)
                    
            except:
                #On ferme la connexion
                print("Deconnexion de {}".format(self.adress))
                active = False
                self.waiter.client_disconnected(self.client)

    def give_info_session(self):
        data = ""
        for i in range(len(self.game_list)):
            data += "{}:{},{} ".format(i, self.game_list[i].nb_joueur,\
                self.game_list[i].status)
        self.client.send(pickle.dumps(data))

    def create_new_game(self, adress):
        self.game_list.append(Game())
        self.game_list[len(self.game_list)-1].ajouter_joueur(self.adress)
        data = "Game:{}_join".format(len(self.game_list)-1)
        self.client.send(pickle.dumps(data))
                

class Game(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.joueur = []
        self.status = "En_attente"
        self.nb_joueur = 0

    def run(self):
        while(self.nb_joueur<2):
            self.status = "En_attente"
            self.nb_joueur = len(self.joueur)
        #Nombre de joueurs requis atteint

    def jouer(self):
        pass

    def ajouter_joueur(self, adress):
        self.joueur.append(adress)

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(('', 12058))

client_connected = []
adress_connected = []
listener_list = []
game_list = []

waiter = Waiter(socket, client_connected, adress_connected, listener_list, game_list)
waiter.start()