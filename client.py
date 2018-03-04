#!/usr/bin/python3
# -*- coding:utf-8 -*-

import math
import time
import socket
import sys
import pickle
from threading import Thread
import sys
if(sys.version[:1]=="3"):
    print("Python 3 detected")
    from tkinter import *
else:
    print("Python 2 detected")
    from Tkinter import *

class server_listener(Thread):

    def __init__(self, connect_socket):
        Thread.__init__(self)
        self.socket = connect_socket
        self.active = 1
        self.msg = ""

    def run(self):
        while self.active:
            try:
                self.msg = pickle.loads(self.socket.recv(4096))
                print(self.msg)
            except:
                self.active = False

    def get_msg(self):
        return self.msg

class server_messager(Thread):
    def __init__(self, connect_socket):
        Thread.__init__(self)
        self.socket = connect_socket

    def send_msg(self, message):
        self.socket.send(pickle.dumps(message))

class Game(Thread):
    def __init__(self, root):
        Thread.__init__(self)
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        try:
            self.socket.close()
        except:
            pass
        self.root.destroy()

    def run(self):
        self.ecran_principal()

    def ecran_principal(self):
        #Affiche l'ecran principal
        self.clean_screen()
        self.jouer = Button(self.root, text="Jouer", command=self.jouer)
        self.jouer.pack()
        self.tester = Button(self.root, text="Tester la connexion", command=self.co_test)
        self.tester.pack()
        self.adress_server = Entry(self.root)
        self.adress_server.insert(END, "localhost")
        self.adress_server.pack()
        self.port_server = Entry(self.root)
        self.port_server.insert(END, "12058")
        self.port_server.pack()

    def ecran_selection_serveur(self):
        #Le time.sleep est la pour que que le thread listener puisse recevoir le message en premier et
        #qu'ensuite seulement le thread game puisse lire le message reçu
        while(self.listener.get_msg().split(" ")[0] != "IG"):
            time.sleep(0.25)
        if(self.listener.get_msg()!=""):
            self.afficher_serveur(self.listener.get_msg())
        #On affiche les boutons de bases
        self.button_create_party = Button(self.root, text="Créer une partie", command=self.create_party)
        self.button_quit_server = Button(self.root, text="Quitter le serveur", command=self.quit_server)
        self.button_create_party.pack()
        self.button_quit_server.pack()

    def ecran_lobby(self):
        #Intruction pour l'affichage de l'ecran
        self.clean_screen()
        lobby_label = Label(self.root, text="Yeah lobby !")
        lobby_label.pack()
        while(self.listener.get_msg().split(" ")[0] != "GD"):
            time.sleep(0.25)
        self.ecran_jeu()

    def ecran_jeu(self):
        #Attente du premier message relatif au jeu les suivants seront lu au fil du jeu et non en l'interromptant
        while(self.listener.get_msg().split(" ")[0] != "GD"):
            time.sleep(0.25)
        self.clean_screen()
        self.canvas = Canvas(self.root, width=450, height=350)
        self.canvas.pack()
        server_quit_button = Button(self.root, text="Quitter le serveur", command=self.quit_server)
        server_quit_button.pack()
        self.mCanon = Canon(self.canvas, 20, 250)
        self.mBoulet = Boulet(self.canvas, 20, 175, 0, 0)
        self.mSol = Sol(self.canvas, 0, 250, 450, 250)
        self.mCanon.draw()
        self.root.after(0, self.animation)

    def get_adress(self):
        return self.adress_server.get()
    def get_port(self):
        return int(self.port_server.get())
    def clean_screen(self):
        for element in self.root.winfo_children():
            element.destroy()
    def afficher_serveur(self, message):
        #split " " pour séparé les parties
        #split : pour le numero de la partie
        #split , pour le nombre de joueur
        #le reste est le statut de la game
        print(message)
        game = message.split(" ")
        self.button_server = []
        print(game)
        for element in game:
            if(len(game)==2):
                break
            elif(element==""):
                pass
            elif(element=="IG"):
                pass
            else:
                print(element)
                buffer_game = element.split(":")
                id_game = buffer_game[0]
                buffer_game = buffer_game[1].split(",")
                nb_joueur = buffer_game[0]
                statut = buffer_game[1]
                self.button_server.append(Button(self.root, text="Id game : {}\nNombre de joueurs : {}\nStatut : {}"\
                    .format(id_game, nb_joueur, statut)\
                    , command=lambda id_button=id_game: self.join_game(id_button)))
        for element in self.button_server:
            element.pack()

    def create_party(self):
        self.messager.send_msg("New party")
        #TODO suite d'instruction pour charger le lobby d'attente de la partie
        self.ecran_lobby()

    def quit_server(self):
        self.socket.close()
        self.clean_screen()
        self.ecran_principal()

    def join_game(self, id_button):
        self.messager.send_msg("Join {}".format(id_button))
        #TODO suite d'instruction pour charger le lobby d'attente de la partie
        active = True
        while active:
            time.sleep(0.25)
            if(self.listener.get_msg().split(' ')[0]=="IC"):
                if("Full" in self.listener.get_msg()):
                    Label(self.root, text="Serveur complet")
                else:
                    active = False
            if(self.listener.get_msg().split(" ")[0]=="IJ"):
                active = False

        self.ecran_lobby()


    def jouer(self):
        #try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.get_adress(), self.get_port()))

            self.listener = server_listener(self.socket)
            self.messager = server_messager(self.socket)
            self.listener.start()
            self.messager.start()

            #On fait une requete au serveur pour savoir il y a une session disponible
            self.messager.send_msg("Info session")
            self.clean_screen()
            self.ecran_selection_serveur()

        #except:
        #   print("Connexion interrompu ou indisponible")
        #   self.ecran_principal()

    def animation(self):
        self.canvas.create_rectangle(0,0,450,350, fill="white")
        self.mCanon.update(self.root.winfo_pointerx()-self.root.winfo_rootx(), self.root.winfo_pointery()-self.root.winfo_rooty())
        self.mBoulet.draw()
        self.mSol.draw()
        self.root.after(500, self.animation)

    def co_test(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.get_adress(), self.get_port()))
            self.socket.send(pickle.dumps("Test"))
            print(pickle.loads(self.socket.recv(1024)))
            self.status = Label(self.root, text="La connexion peut etre etabli")
            self.status.pack()
            self.socket.close()
        except:
            self.status = Label(self.root, text="La connexion ne peut pas etre etabli")
            self.status.pack()

class Canon:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.height = 30
        self.width = 15

    def draw(self):
        self.canvas.create_rectangle(self.x-self.width/2, self.y, self.x+self.width/2, self.y-self.height)
    def update(self, mouse_x, mouse_y):
        print(str(mouse_x)+" "+str(mouse_y))
        self.canvas.create_rectangle(self.x-self.width/2, self.y, self.x+self.width/2+math.cos(self.x-mouse_x), self.y-self.height+math.sin(self.y-mouse_y))

class Boulet:
    def __init__(self, canvas, x ,y, vx, vy):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.rayon = 10

    def draw(self):
        self.canvas.create_oval(self.x-self.rayon/2, self.y-self.rayon/2, self.x+self.rayon/2, self.y+self.rayon/2, fill="black")

class Sol:
    def __init__(self, canvas, x1, y1, x2, y2):
        self.canvas = canvas
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def draw(self):
        self.canvas.create_line(self.x1, self.y1, self.x2, self.y2, fill="black")

root = Tk()
game = Game(root)
game.start()
root.mainloop()