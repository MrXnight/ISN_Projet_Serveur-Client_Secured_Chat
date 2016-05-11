import socket #On importe les bibliothèques nécessaires pour la programmation en parallèle et les connexions 
from threading import Thread
import sys
import os
import _thread
#On définit l'objet threadClient qui va servir à ouvrir une connexion entre le client et le serveur à chaque fois qu'un client essaye de se connecter
class threadClient(Thread):
    def __init__(self,socketclient):
        Thread.__init__(self)
        self.msg=""
        self.name=self.getName()
        self.socketclient=socketclient
        self.kill=False
    def run(self): # Boucle qui va se lancer lorqu'un client se connecte, elle va attendre les messages du client pour lequel elle a été créé.
        global serveur
        global connexion_ecoute
        while(self.kill==False and serveur==True): 
            msg=self.socketclient.recv(65536)
            print(msg.decode())
            if(msg.decode()=="\\ZmVybWVy"):
                del liste_pseudo[self.socketclient]
                del client_connecte[self.name]
                self.socketclient.close()
                self.kill=True
            elif(msg.decode()=="/shutdown"):
                for envoi in client_connecte: #Elle envoie ensuite le message reçu à chaque client connectée
                    client_connecte[envoi].send("/shutdown".encode())
                    client_connecte[envoi].close()
                connexion_ecoute.close()
                serveur=False
            else:
                for envoi in client_connecte: #Elle envoie ensuite le message reçu à chaque client connectée
                    client_connecte[envoi].send(msg)
connexion_ecoute = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #On paramètre le port où le serveur va écouter pour la connexion de client et le type de connexion qui va être utilisé
connexion_ecoute.bind(("",27015)) #On écoute sur l'adresse locale sur le port 27015
connexion_ecoute.listen(5) #On lance l'écoute et on accepte maximum 5 clients
connexion_ecoute.settimeout(1)
print("Serveur à l'écoute en attente de connexion")
client_connecte={}
liste_pseudo={}
demandePseudo=""
serveur=True
while(serveur==True):
    presence_pseudo=False
    try:
        socket,infos_connexion=connexion_ecoute.accept() #Boucle de d'écoute du serveur qui accepete les demandes de connexions des clients et qui crée un thread décrit plus haut pour chacun d'entre eux
    except:
        print("pas de connexion")
    else:
        print("Connexion du client(%s)"%infos_connexion[0])
        demandePseudo=socket.recv(65536)
        demandePseudo=demandePseudo.decode()
        for psd in liste_pseudo.values():
            if(psd==demandePseudo):
                socket.close()
                presence_pseudo=True
        if(presence_pseudo==False):
            liste_pseudo[socket]=demandePseudo
        newClient_thread=threadClient(socket) #On crée le thread
        newClient_thread.start() #On lance le thread
        name=newClient_thread.getName()
        client_connecte[name]=socket
        print(liste_pseudo)



 

