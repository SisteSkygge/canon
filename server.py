#!/usr/bin/python3
# -*- coding:utf-8 -*-

import socket
from threading import Thread
import pickle
import time

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
                    #Un joueur test si le serveur est online, on lui renvoie une réponse
                    self.client.send(pickle.dumps("Ok"))
                if(self.msg=="Info session"):
                    #Le joueur vient de se connecter on lui envoie les informations des parties existantes
                    print("Envoie des informations...")
                    self.give_info_session()
                if(self.msg=="New party"):
                    #Le joueur veut créer une partie
                    print("Création d'une nouvelle partie...")
                    self.create_new_game(self.adress)
                if("Join" in self.msg):
                    #Le joueur veut rejoindre une partie
                    id_game = self.msg.split(" ")[1]
                    if(self.game_list[int(id_game)].nb_joueur<2):
                        #Il y a de la place
                        self.client.send(pickle.dumps("IC Game:{}_join".format(id_game)))
                        self.game_list[int(id_game)].ajouter_joueur(self.adress, self)
                    else:
                        #Il y a plus de place
                        self.client.send(pickle.dumps("IC Full"))
                    
            except:
                #On ferme la connexion
                print("Deconnexion de {}".format(self.adress))
                active = False
                self.deco_client_from_game()
                self.waiter.client_disconnected(self.client)

    def give_info_session(self):
        data = "IG "
        for i in range(len(self.game_list)):
            data += "{}:{},{} ".format(i, self.game_list[i].nb_joueur,\
                self.game_list[i].status)
        self.client.send(pickle.dumps(data))

    def create_new_game(self, adress):
        self.game_list.append(Game())
        self.game_list[len(self.game_list)-1].start()
        self.game_list[len(self.game_list)-1].ajouter_joueur(self.adress, self)
        data = "IC Game:{}_join".format(len(self.game_list)-1)
        self.client.send(pickle.dumps(data))

    def deco_client_from_game(self):
        for element in self.game_list:
            for i in range(len(element.joueur)):
                if(self.adress==element.joueur[i]):
                    del element.joueur[i]
                

class Game(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.joueur = []
        self.joueur_listener = []
        self.status = "En_attente"
        self.nb_joueur = 1

    def run(self):
        self.lobby()

    def lobby(self):
        while(self.nb_joueur<2):
            time.sleep(0.25)
            self.status = "En_attente"
            self.nb_joueur = len(self.joueur)
            self.send_info_lobby_joueur()
        compteur = 0
        while(self.nb_joueur==2 and compteur<20):
            time.sleep(0.25)
            self.send_info_lobby_joueur()
            self.status = "Complet"
            self.nb_joueur = len(self.joueur)
            compteur += 1

    def jouer(self):
        canon = []
        sol = []
        boulet = []
        canon.append(Joueur(0, 20, 250))
        canon.append(Joueur(1, 430, 250))
        sol.append(Sol(0, 250, 450, 250))
        while(self.nb_joueur==2):
            self.nb_joueur = len(self.joueur)    
            self.send_info_jeu(canon, boulet, sol)
        #On affiche qui a gagne on fait un petit compteur puis on supprime la partie en supprimant les deux joueurs
        #Comme le nombre de joueurs sera à 0 le game_cleaner supprimera la game
        del self.joueur[0]
        del self.joueur[1]
        self.nb_joueur = len(self.joueur)

    def ajouter_joueur(self, adress, joueur_listener):
        self.joueur.append(adress)
        self.joueur_listener.append(joueur_listener)

    def send_info_lobby_joueur(self):
        data = "IJ "
        for element in self.joueur:
            data += str(element)+" "
        if(self.nb_joueur==2):
            data += "GO"
        for element in self.joueur_listener:
            element.client.send(pickle.dumps(data))

    def send_info_jeu(self, canon, boulet, sol):
        #Envoie les informations necessaire à tout les joueurs
        data = "GD "
        for element in canon:
            data += element.return_info()
        for element in boulet:
            data += element.return_info()
        for element in sol:
            data += element.return_info()

        for element in self.joueur_listener:
            element.client.send(pickle.dumps(data))

class Game_Cleaner(Thread):
    def __init__(self, game_list):
        Thread.__init__(self)
        self.game_list = game_list

    def run(self):
        while True:
            time.sleep(0.25)
            for i in range(len(self.game_list)):
                if(self.game_list[i].nb_joueur==0):
                    del self.game_list[i]

class Joueur:
    def __init__(self, num, x, y):
        self.num = num
        self.x = x
        self.y = y
        self.width = 15
        self.height = 30

    def return_rectangle(self):
        x1 = self.x-self.width/2
        y1 = self.y
        x2 = self.x+self.width/2
        y2 = self.y-self.height
        return (x1,y1,x2,y2)

    def return_info(self):
        info = self.return_rectangle()
        data = "canon:{},{},{},{} ".format(info[1], info[2], info[3], info[4])
        return data

class Boulet:
    def __init__(self, x, y):
        self.rayon = 30
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0

    def return_rectangle(self):
        #Servira pour la hitbox
        x1 = self.x-self.rayon/2
        y1 = self.y-self.rayon/2
        x2 = self.x+self.rayon/2
        y2 = self.y+self.rayon/2
        return (x1,y1,x2,y2)

    def deplacement(self):
        self.x += vx
        self.y += vy
        self.vy -= 5

    def return_info(self):
        data = "boulet:{},{},{},{} ".format(self.x, self.y, self.vx, self.vy)
        return data

class Sol:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def return_info(self):
        data = "sol:{},{},{},{} ".format(self.x1, self.y1, self.x2, self.y2)
        return data


socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(('', 12058))

client_connected = []
adress_connected = []
listener_list = []
game_list = []

waiter = Waiter(socket, client_connected, adress_connected, listener_list, game_list)
waiter.start()
game_cleaner = Game_Cleaner(game_list)
game_cleaner.start()