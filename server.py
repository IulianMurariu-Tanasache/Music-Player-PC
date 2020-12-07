import pygame
import os
import time as timp
from mutagen.mp3 import MP3
import math
import random
import socket
import threading
import select
from main import *

header = 32
FORMAT = 'utf-8'
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER,PORT)
disconnect = 'out!'
clients = []

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#server.setblocking(False)
server.bind(ADDR)
print(SERVER)

def send_data(conn,msg):
    message = msg.encode(FORMAT)
    length = len(message)
    send_length = (str(length)  + " " * (header - len(str(length)))).encode(FORMAT)
    conn.send(send_length)
    conn.send(message)

class Check:
    def __init__(self,addr):
        self.ishere = True
        self.connected = True
        self.addr = addr
    def check(self,conn):
        while self.ishere:
            if self.ishere:
                try:
                    send_data(conn,'check')
                    print("Sent check")
                except:
                    return
                self.ishere = False
                timp.sleep(30)
        print(f'Connection timed out with {self.addr}!')
        self.connected = False


def handle_client(conn,addr):
    print(f'Connected with address: {addr}')
    clients.append(conn);
    connected = True
    timp.sleep(1)
    msg = State.__getstate__()
    send_data(conn,msg)
    msg = ''
    checking = Check(addr)
    thread_check = threading.Timer(30,checking.check,args=(conn,))
    thread_check.start()
    read = [conn]
    write = []
    errors = []
    while checking.connected:
        to_read,to_write,errs = select.select(read,write,errors,30)
        if to_read and checking.connected:
            msg = conn.recv(header).decode(FORMAT)
            #print("Received: " + msg)
            if msg:
                if msg == 'here':
                    checking.ishere = True
                    print(f'{checking.addr} is still here!')
                else:
                    msg_length = int(msg)
                    msg = conn.recv(msg_length).decode(FORMAT)
                    print(f'Received message: {msg}')
                    if msg == disconnect:
                        checking.connected = False
                    else:
                        State.update(msg)
                        data = State.__getstate__()
                        for connect in clients:
                            send_data(connect,data)

    print(f'Closing connection with {checking.addr}!')
    clients.remove(conn)
    del checking
    with open('data.json', 'w') as data:
        print('Updating!')
        jsonstring = State.__getstate__()
        data.seek(0)
        data.write(jsonstring)
    conn.close()

def start():
    server.listen()
    while True:
        conn,addr = server.accept()
        thread = threading.Thread(target=handle_client,args=(conn,addr))
        thread.start()
        print(f'Conected clients: {threading.active_count() - 1}')

class State:
    currentSong = ''
    index = -1
    prevIndex = -1
    cTime = 0
    songLength = -1
    paused = True
    songbuttons = []
    repeat = 0
    shuffle = False
    playlists = []
    playlistIndex = -1
    allsongs = True
    switched = False
    prevplaylist = -1
    renamelist = False
    toadd = False
    _songbar = None
    _playsong = None

    @classmethod
    def __getstate__(cls):
        data = 'currentSong: ' + cls.currentSong + '\nindex: ' + str(cls.index) + '\nprevIndex: ' + str(cls.prevIndex) + '\ncTime: ' + str(cls.cTime) + '\nsongLength: ' + str(cls.songLength) + '\npaused: ' + str(cls.paused) + '\nrepeat: ' + str(cls.repeat) + '\nshuffle: ' + str(cls.shuffle) + '\nplaylistIndex: ' + str(cls.playlistIndex)  # +'prevplaylist' + cls.prevplaylist
        return data

    @classmethod
    def update(cls, s):
        j = 0;
        data = s.split('\n')
        while j < len(data):
            i = data[j].find(' ')
            str = data[j][i + 1:len(data[j])]
            if j == 0:
                cls.currentSong = str
            elif j == 1:
                cls.index = int(str)
            elif j == 2:
                cls.prevIndex = int(str)
            elif j == 3:
                cls.cTime = int(float(str))
            elif j == 4:
                cls.songLength = int(float(str))
            elif j == 5:
                cls.pause = bool(str)
            elif j == 6:
                cls.repeat = int(str)
            elif j == 7:
                cls.shuffle = bool(str)
            elif j == 8:
                cls.prevplaylist = int(str)
            j = j + 1

def update_data():
    while True:
        timp.sleep(20)
        with open('data.json','w') as data:
            print('Updating!')
            jsonstring = State.__getstate__()
            data.seek(0)
            data.write(jsonstring)

def load_data():
    print(os.getcwd())
    with open('data.json', 'r') as data:
        s = data.readlines();
        message = ""
        for str in s:
            message += str
        if message:
            State.update(message)
def run():
    print('Loading data...')
    load_data()
    print('Server is starting...')
    start_thread = threading.Thread(target=start,args=())
    start_thread.start()
    update_thread = threading.Thread(target=update_data,args=())
    update_thread.start()

run()