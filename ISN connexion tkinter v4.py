import socket
from tkinter import *
from tkinter.messagebox import * 
from threading import Thread
import time
import sys
import _thread
import base64

class receptServ(Thread):  # Thread réception message
    def __init__(self):
        Thread.__init__(self)
        self.msg=""
        self.kill=False
    def run(self):
        global chat
        while(self.kill==False):
            self.msg=connexion_serveur.recv(1024)
            self.msg=self.msg.decode()
            if(self.msg=="/shutdown"):
                time.sleep(1)
                connexion_serveur.close()
                chat.fen.destroy()
                self.kill=True
            elif(self.msg=="/img"):
                print(self.msg)
                self.msg=connexion_serveur.recv(65536)
                print(self.msg)
                self.fichierImg = open("imageDownld.png", "wb")
                self.fichierImg.write(base64.decodestring(self.msg))
                self.fichierImg.close()
            else:
                chat.afficherTxt(self.msg)

            
class InterfaceDemande():
    def __init__(self): #Définition fenêtre paramétrage connexion
        self.fen=Tk()
        self.defHote=StringVar()
        self.defHote.set("192.168.1.1") #valeur de base ip
        self.defPort=IntVar()
        self.defPort.set(15000) 
        self.demandeHote=Entry(self.fen,textvariable=self.defHote) #case demande ip de connexion
        self.demandeHote.pack()
        self.demandePort=Entry(self.fen,textvariable=self.defPort) #case demande port
        self.demandePort.pack()
        self.demandePseudo=Entry(self.fen)
        self.demandePseudo.pack()
        self.valider=Button(self.fen,text="valider",command=self.connexion) 
        self.fen.bind("<Return>",self.connexionEntry)
        self.valider.pack()
    def connexionEntry(self,event): #event entrer envoyer le msg
        self.connexion()
    def connexion(self): #Connexion au serveur
        global hote
        global port
        global connexion_serveur
        global connexion
        hote=self.demandeHote.get()
        port=int(self.demandePort.get())
        connexion_serveur=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            connexion_serveur.connect((hote,port))
        except:
            showerror("Erreur","Le client n'a pas pu se connecter")
        else:
            self.pseudo()
            connexion=True
            self.fen.destroy()
    def pseudo(self):
        global pseudo
        self.pseudo=self.demandePseudo.get()
        connexion_serveur.send(self.pseudo.encode())
        pseudo=self.pseudo
    def run(self):
        self.fen.mainloop()

        
class InterfaceChat(): #Fenetre de chat
    def __init__(self):
        self.fen=Tk()
        self.chat=Text(self.fen,height=25,width=50,wrap='word',takefocus=0)
        self.chat.grid(row=0,columnspan=3)
        self.chat.bind("<KeyPress>",lambda e:"break")
        self.txtEnvoi=Entry(self.fen,width=40)
        self.txtEnvoi.grid(row=1,padx=10,pady=10)
        self.txtEnvoi.bind("<Return>",self.envoyerMessageEntry)
        self.envoi=Button(self.fen,text="Envoyer",command=self.envoyerMessage,width=10)
        self.envoi.grid(row=1,column=1,padx=2,pady=5)
        self.boutonQuitter=Button(self.fen,text="Quitter",command=self.quitter,width=10)
        self.boutonQuitter.grid(row=1,column=2,padx=10,pady=10)
        self.thread_reception=receptServ()
        self.thread_reception.start()
    def envoyerMessage(self): #Fonction envoyer message
        self.msg_a_envoyer=self.txtEnvoi.get()
        if(self.msg_a_envoyer!=""):
            if(self.msg_a_envoyer[0]=="/"):
                if(self.msg_a_envoyer[0:4]=="/img"):
                    self.envoyerImg(self.msg_a_envoyer[5:])
                else:    
                    self.msg_a_envoyer=self.msg_a_envoyer.encode()
                    print(self.msg_a_envoyer)
                    connexion_serveur.send(self.msg_a_envoyer)
                    self.txtEnvoi.delete(0,END)
            else:
                self.msg_a_envoyer=pseudo+" : " +self.msg_a_envoyer
                self.msg_a_envoyer=self.msg_a_envoyer.encode()
                print(self.msg_a_envoyer)
                connexion_serveur.send(self.msg_a_envoyer)
                self.txtEnvoi.delete(0,END)
    def envoyerMessageEntry(self,event): #Envoyer 
        self.envoyerMessage()
    def envoyerImg(self,chemin):
        with open(chemin, "rb") as imageFile:
            self.message = base64.b64encode(imageFile.read())
            connexion_serveur.send(("/img").encode())
            connexion_serveur.send(self.message)
            self.txtEnvoi.delete(0,END)
    def quitter(self):
        connexion_serveur.send("\\ZmVybWVy".encode())
        self.thread_reception.kill=True
        time.sleep(1)
        connexion_serveur.close()
        self.fen.destroy()
    def afficherTxt(self,text):
        self.chat.insert(END,text+"\n")
        print(text)
    def run(self):
        self.fen.mainloop()

        
hote="";port="";connexion=False;pseudo=""
fenetreDemande=InterfaceDemande()
fenetreDemande.run()
if(connexion==True):
    chat=InterfaceChat()
    chat.run()
