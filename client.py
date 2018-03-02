#!/usr/bin/python3
# -*- coding:utf-8 -*-

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
        #Affiche l'ecran de selection de la partie
        if(self.listener.get_msg()!=""):
            #Dans le cas ou cest pas vide on affiche les parties
            pass
        #On affiche les boutons de bases
        self.button_create_party = Button(self.root, text="Créer une partie", command=self.create_party)
        self.button_quit_server = Button(self.root, text="Quitter le serveur", command=self.quit_server)
        self.button_create_party.pack()
        self.button_quit_server.pack()

    def get_adress(self):
        return self.adress_server.get()
    def get_port(self):
        return int(self.port_server.get())
    def clean_screen(self):
        for element in self.root.winfo_children():
            element.destroy()

    def create_party(self):
        self.messager.send_msg("New party")

    def quit_server(self):
        self.socket.close()
        self.clean_screen()
        self.ecran_principal()

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

root = Tk()
game = Game(root)
game.start()
root.mainloop()