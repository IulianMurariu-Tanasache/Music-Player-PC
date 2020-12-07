import pygame
import os
import time as timp
from mutagen.mp3 import MP3
import math
import random
import socket
import threading

colors = {
    'white': (255, 255, 255),
    'lightgrey': (155, 155, 155),
    'grey': (105, 105, 105),
    'black': (0, 0, 0)
}

class State:
    happened = False
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
    _listbar = None

    @classmethod
    def __getstate__(cls):
        data = 'currentSong: ' + cls.currentSong + '\nindex: ' + str(cls.index) + '\nprevIndex: ' + str(
            cls.prevIndex) + '\ncTime: ' + str(cls.cTime) + '\nsongLength: ' + str(cls.songLength) + '\npaused: ' + str(
            cls.paused) + '\nrepeat: ' + str(cls.repeat) + '\nshuffle: ' + str(cls.shuffle) + '\nplaylistIndex: ' + str(
            cls.playlistIndex)  # +'prevplaylist' + cls.prevplaylist
            #'allsongs' : cls.allsongs+
            #'switched' : cls.switched+

            #'renamelist' : cls.renamelist+
            #'toadd' : cls.toadd+
        return data

    @classmethod
    def update_realtime(cls):
        if not State.allsongs:
            State.index = State.index % len(State.playlists[State.playlistIndex].songs)
            song = State.playlists[State.playlistIndex].songs[State.index].name
            if State.prevIndex != -1:
                State.playlists[State.playlistIndex].songs[State.prevIndex].img = State._songbar
            State.playlists[State.playlistIndex].songs[State.index].img = State._playsong
        else:
            State.index = State.index % len(State.songbuttons)
            song = State.songbuttons[State.index].name
            if State.prevIndex != -1:
                State.songbuttons[State.prevIndex].img = State._songbar
            State.songbuttons[State.index].img = State._playsong
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()
        if State.paused:
            pygame.mixer.music.pause()

        State.songLength = MP3(song).info.length

    @classmethod
    def update(cls, s):
        j = 0;
        data = s.split('\n')
        while j < len(data):
            i = data[j].find(' ')
            str = data[j][i+1:len(data[j])]
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
        cls.update_realtime()
        # i = 0
        # for p in s.playlists:
        #     cls.playlists.append(Playlist(cls._listbar))
        #     try:
        #         cls.playlists[len(cls.playlists) - 1].button.textname = p.button.textname
        #     except:
        #         try:
        #             print(p)
        #             cls.playlists[len(cls.playlists) - 1].button.textname = p['button']['textname']
        #         except:
        #             cls.playlists[len(cls.playlists) - 1].button.textname = 'scz nuj ce are'
        #             print('ai belit-o')
        #     try:
        #         for song in p.songs:
        #             cls.playlists[i].songs.append(Button(song.x,song.y,song.index,State._songbar,0,0,'black',song.name,(20,24)))
        #             i += 1
        #     except:
        #         pass
        # cls.playlistIndex = s.playlistIndex
        # #cls.allsongs = s.allsongs
        # #cls.switched = s.switched
        # cls.prevplaylist = s.prevplaylist
        # #cls.renamelist = s.renamelist
        # #cls.toadd = s.toadd


class Client:
    header = 32
    FORMAT = 'utf-8'
    PORT = 5050
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDR = (SERVER, PORT)
    disconnect = 'out!'
    offline = True

    def __init__(self):
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.client.connect(self.ADDR)
            self.offline = False
            print('Connected to server!')
        except:
            print('Running offline!')

    def send(self,msg):
        if self.offline:
            return
        try:
            message = msg.encode(self.FORMAT)
            length = len(message)
            send_length = str(length).encode(self.FORMAT)
            send_length += b' ' * (self.header - len(send_length))
            self.client.send(send_length)
            self.client.send(message)
            print('Sent message!')
        except:
            self.offline = True

    def send_state(self):
        if self.offline:
            return
        State.happened = False
        msg = State.__getstate__()
        send_thread = threading.Thread(target=self.send, args=(msg,))
        send_thread.start()


    def load(self):
        if self.offline:
            return
        msg = self.client.recv(self.header).decode(self.FORMAT)
        if msg and msg != 'check':
            msg_length = int(msg)
            msg = self.client.recv(msg_length).decode(self.FORMAT)
            print('Received data!')
            State.update(msg)

    def respondCheck(self):
        if self.offline:
            return
        def respond():
            while True:
                try:
                    msg = self.client.recv(self.header).decode(self.FORMAT)
                except:
                    self.offline = True
                    return
                if msg == 'check':
                    msg = 'here'
                    msg = msg.encode(self.FORMAT)
                    try:
                        self.client.send(msg)
                    except:
                        self.offline = True
        thread_respond = threading.Timer(30,respond)
        thread_respond.start()

    def load_data(self):
        load_thread = threading.Thread(target=self.load, args=())
        load_thread.start()

def play():
    if not State.allsongs:
        State.index = State.index % len(State.playlists[State.playlistIndex].songs)
        song = State.playlists[State.playlistIndex].songs[State.index].name
        if State.prevIndex != -1:
            State.playlists[State.playlistIndex].songs[State.prevIndex].img = State._songbar
        State.playlists[State.playlistIndex].songs[State.index].img = State._playsong
    else:
        State.index = State.index % len(State.songbuttons)
        song = State.songbuttons[State.index].name
        if State.prevIndex != -1:
            State.songbuttons[State.prevIndex].img = State._songbar
        State.songbuttons[State.index].img = State._playsong
    pygame.mixer.music.load(song)
    State.paused = False
    State.currentSong = song
    State.cTime = timp.process_time() - State.cTime
    State.songLength = MP3(song).info.length
    print(State.songLength)
    pygame.mixer.music.play()

def stop(time):
    State.index = -1
    pygame.mixer_music.stop()
    time.setPosCircle(time.x + time.imgbar.x)
    time.setTime()
    State.currentSong = ''

def pause(time):
    if not State.paused:
        pygame.mixer.music.pause()
        time.setTime()
    else:
        pygame.mixer.music.unpause()
        State.cTime = timp.process_time()
    State.paused = not State.paused


def next():
    State.prevIndex = State.index
    if State.switched:
        State.switched = False
        if State.allsongs and State.prevplaylist != -1:
            State.playlists[State.prevplaylist].songs[State.index].img = State._songbar
        elif not State.allsongs:
            State.songbuttons[State.index].img = State._songbar
        State.prevIndex = -1
        State.index = -1
    if not State.shuffle:
        State.index = State.index + 1
    else:
        while State.index == State.prevIndex:
            if State.allsongs:
                State.index = random.randrange(0, len(State.songbuttons))
            else:
                State.index = random.randrange(0, len(State.playlists[State.playlistIndex].songs))
            print(State.index)
    play()


def previous():
    if State.switched:
        State.switched = False
        if State.allsongs and State.prevplaylist != -1:
            State.playlists[State.prevplaylist].songs[State.index].img = State._songbar
            print('da')
        elif not State.allsongs:
            State.songbuttons[State.index].img = State._songbar
            print('da')
        State.prevIndex = -1
        State.index = -1
    if not State.shuffle:
        State.prevIndex = State.index
        if State.index != -1:
            State.index = State.index - 1
    else:
        State.index = State.prevIndex
    play()


def shuffle():
    State.shuffle = not State.shuffle
    random.seed()


def repeat():
    State.repeat = (State.repeat + 1) % 3


def allsongs(songview):
    songview.reset(12, len(State.songbuttons))
    songview.setPosCircle(songview.y)
    State.allsongs = True
    State.prevplaylist = State.playlistIndex
    State.playlistsIndex = -1
    State.switched = True

def add():
    if State.index == -1:
        return
    State.toadd = True

def remove(songview,time):
    if State.allsongs or len(State.playlists[State.playlistIndex].songs) == 0 :
        return
    for b in State.playlists[State.playlistIndex].songs:
        if b.name == State.currentSong:
            State.playlists[State.playlistIndex].songs.remove(b)
    songview.update(len(State.playlists[State.playlistIndex].songs))
    for i in range(0, len(State.playlists[State.playlistIndex].songs)):
        if songview.list[i]:
            State.playlists[State.playlistIndex].songs[i].update(i - songview.value)
            State.playlists[State.playlistIndex].songs[i].draw(window)
    stop(time)


def renamelplaylist():
    State.renamelist = True


def newplaylist():
    State.playlists.append(Playlist(State._listbar))


def deleteplaylist(songview,time):
    if State.playlistIndex != -1:
        del State.playlists[State.playlistIndex]
        for i in range(State.playlistIndex, len(State.playlists)):
            State.playlists[i].button.update(i)
        State.playlistIndex = -1
        allsongs(songview)
        stop(time)

def cutText(text,w):
    tw,th = font.size(text)
    lw,lh = font.size('_')
    i = math.ceil((tw - w) / lw)
    if i <= 0:
        return text
    text = text[:-i- 3] + '...'
    return text

class Image:
    def __init__(self,img,x,y,w,h):
        self.img = img
        self.w = w
        self.h = h
        self.x = x
        self.y = y

    def resize(self,w=0,h=0):
        if w == 0 and h == 0:
            w = int(1280 / 1920 * self.img.get_width())
            h = int(1280 / 1920 * self.img.get_height())
            self.img = pygame.transform.smoothscale(self.img, (w,h))
            self.w = int(1280 * self.w / 1920)
            self.h = int(1280 * self.h / 1920)
            self.x = int(1280 * self.x / 1920)
            self.y = int(1280 * self.y / 1920)
        else:
            self.x = int(self.x * w / self.w)
            self.y = int(self.y * h / self.h)
            self.w = int(self.img.get_width() * w / self.w)
            self.h = int(self.img.get_height() * h / self.h)
            self.img = pygame.transform.smoothscale(self.img, (self.w, self.h))
            self.w = w
            self.h = h

class Playlist:
    def __init__(self,img):
        self.index = len(State.playlists)
        self.button = Button(5, 60,self.index,img,0,30, 'black', 'playlist ' + str(self.index),(17,24))
        self.songs = []


class Button:
    def __init__(self, x, y, i, img , w = 0, h = 0, color="", name="",textpos = (0,0)):
        self.index = i
        self.textpos = textpos
        self.x = x
        self.y = y
        self.img = img
        if h != 0 and w != 0:
            self.img.resize(w, h)
        self.h = self.img.h
        self.w = self.img.w
        self.name = name
        self.textname = cutText(name, self.img.w)
        self.color = color
        if color == '':
            self.color = 'white'

    def draw(self, window):
        window.blit(self.img.img,(self.x, self.index * (self.h+5) + self.y))
        text = font.render(f"{self.textname}", 1, colors[self.color])
        window.blit(text, (self.x + self.textpos[0], self.index * (self.h + 5) + self.y + self.textpos[1]))
        #pygame.draw.rect(window,(255,255,255),(self.x+self.img.x,self.index * (self.h + 5) + self.y+self.img.y,self.img.w,self.img.h))

    def update(self, i):
        self.index = i

    def isMouseOn(self):
        mouseX, mouseY = pygame.mouse.get_pos()
        if self.x + self.img.x <= mouseX <= self.img.x + self.x + self.w and self.img.y + self.index * (self.h+5) + self.y <= mouseY <= self.img.y + self.index * (self.h+5) + self.y + self.h:
            return True
        return False

class Slider:
    def __init__(self, x, y,imgbar ,imgball ,w = 0, h = 0,):
        self.imgbar = imgbar
        self.imgball = imgball
        self.x = x
        self.y = y
        if h != 0 and w != 0:
            image = Image(imgbar.img,imgbar.x,imgbar.y,imgbar.w,imgbar.h)
            image.resize(w,h)
            self.imgbar = image
            image = Image(imgball.img, imgball.x,imgball.y,imgball.w, imgball.h)
            image.resize(h+10, h+10)
            self.imgball = image
        self.h = self.imgbar.h
        self.w = self.imgbar.w
        self.radius = int(imgball.h / 2)
        self.center = (self.x + self.imgball.x + self.radius , self.y + self.radius + self.imgball.y)
        self.value = 0
        self.cx = x + self.imgball.x - self.radius
        self.newtime = 0

    def draw(self, window):
        window.blit(self.imgbar.img, (self.x, self.y))
        window.blit(self.imgball.img, (self.cx,self.y + self.imgbar.y - self.imgball.y - int(self.imgbar.h / 2)))
        #pygame.draw.rect(window, (255, 255, 255),
        #(self.x + self.imgbar.x,self.y + self.imgbar.y, self.imgbar.w, self.imgbar.h))

    def isMouseOnRect(self):
        mouseX, mouseY = pygame.mouse.get_pos()
        if self.x + self.imgbar.x <= mouseX <= self.imgbar.x + self.x + self.w and self.imgbar.y + self.y <= mouseY <= self.imgbar.y + self.y + self.h:
            return True
        return False

    def setPosCircle(self, x):
        if self.x + self.imgbar.x <= x <= self.x + self.w + self.imgbar.x:
            self.center = (x + self.imgball.x + self.radius , self.y + self.radius + self.imgball.y)
            self.cx = x - self.imgball.x - self.radius
            self.value = (x - self.x - self.imgbar.x) / (self.w / 100)

    def setVolume(self):
        pygame.mixer.music.set_volume(self.value / 100)

    def setTime(self):
        self.newtime = self.value * State.songLength / 100
        if pygame.mixer_music.get_busy():
            pygame.mixer.music.set_pos(self.newtime)
        State.cTime = timp.process_time()

    def getTime(self, time):
        c = timp.process_time() - State.cTime + self.newtime
        self.value = c * 100 / State.songLength
        self.cx = int(self.value * self.w / 100) + self.x
        self.center = (self.cx + self.x + self.radius, self.y + self.radius)
        if self.value >= 99.5:
            if State.repeat == 0:
                    next()
                    time.setPosCircle(time.x + time.imgbar.x)
                    time.setTime()
            elif State.repeat > 0:
                play()
                time.setPosCircle(time.x + time.imgbar.x)
                time.setTime()
                if State.repeat == 1:
                    State.repeat = State.repeat - 1


class ScrollView:
    def __init__(self, x, y, rows, n ,imgbar , imgball,w = 0):
        self.imgbar = imgbar
        self.imgball = imgball
        self.rows = rows
        self.total = n
        self.list = [False] * n
        if n < rows:
            rows = n - 1
        for i in range(0, rows + 1):
            self.list[i] = True
        self.x = x
        self.y = y
        self.h = imgbar.h
        self.w = w
        self.scrolly = y
        self.barw = imgbar.w
        self.value = 0

    def draw(self, window):
        window.blit(self.imgbar.img, (self.x, self.y))
        window.blit(self.imgball.img, (self.x  - self.imgball.x + self.imgbar.x, self.scrolly - self.imgball.y - int(self.imgball.h/2)))
    def isMouseOnBar(self):
        mouseX, mouseY = pygame.mouse.get_pos()
        if self.x + self.imgbar.x <= mouseX <= self.imgbar.x + self.x + self.barw and self.y + self.imgbar.y <= mouseY <= self.imgbar.y + self.y + self.h:
            return True
        return False

    def setPosCircle(self, y):
        if self.y <= y <= self.y + self.h:
            self.value = math.floor((y - self.y) / self.h * (self.total - self.rows))
            if self.value > self.total - self.rows - 1:
                self.value = self.total - self.rows - 1
                return
            self.scrolly = y

    def update(self, n=-1):
        if n != -1:
            if n > self.total:
                for i in range(self.total,n):
                    self.list.append(False)
            if n < self.total:
                for i in range(n,self.total):
                    self.list.pop()
            self.total = n
        for i in range(0, self.total):
            if self.value <= i <= self.value + self.rows:
                self.list[i] = True
            else:
                self.list[i] = False

    def reset(self,rows,n):
        self.total = n
        self.rows = rows
        if n <= rows:
            self.total = rows + 1
        self.list = [False] * self.total
        for i in range(0, self.rows + 1):
            self.list[i] = True
        self.value = 0

def selectSong(time, i):
    State.prevIndex = State.index
    if State.switched:
        State.switched = False
        if State.allsongs and State.prevplaylist != -1:
            try:
                State.playlists[State.prevplaylist].songs[State.index].img = State._songbar
            except:
                State.songbuttons[State.index].img = State._songbar
                print('nu pot schimba current_song_bar in playlist...probabil nu is melodii in playlist si mie sila sa fac ceva la chestia asta asa ca am pus doar sa treaca peste cu mesajul asta...daca il vezi trolezi xD')
            print('da')
        elif not State.allsongs:
            State.songbuttons[State.index].img = State._songbar
            print('da')
        State.prevIndex = -1
    State.index = i
    play()
    time.setPosCircle(time.x + time.imgbar.x)
    time.setTime()

def main():
    client = Client()
    client.load_data()
    client.respondCheck()
    _background = pygame.image.load('UI/back.png')
    _background = pygame.transform.scale(_background,window_dim)
    _net = pygame.image.load('UI/net.png')
    _net = pygame.transform.smoothscale(_net,(50,45))
    _nonet  = pygame.image.load('UI/nonet.png')
    _nonet = pygame.transform.smoothscale(_nonet,(50,45))
    _shuffle = pygame.image.load('UI/shuffle.png')
    _shuffle = Image(_shuffle,35,40,104,90)
    _shuffle.resize()
    _shufflecopy = pygame.image.load('UI/shuffle.png')
    _shufflecopy = Image(_shufflecopy, 35, 40, 104, 90)
    _shufflecopy.resize()
    _next = pygame.image.load('UI/next.png')
    _next = Image(_next,35,40,104,90)
    _next.resize()
    _pause = pygame.image.load('UI/pause.png')
    _pause = Image(_pause,35,40,104,90)
    _pause.resize()
    _play = pygame.image.load('UI/play.png')
    _play = Image(_play,35,40,104,90)
    _play.resize()
    State._playsong = pygame.image.load('UI/playingsong.png')
    State._playsong = Image(State._playsong, 28, 28, 1097, 38)
    State._playsong.resize()
    State._playsong.resize(State._playsong.w,28)
    _previous = pygame.image.load('UI/previous.png')
    _previous = Image(_previous,35,40,104,90)
    _previous.resize()
    _repeat = pygame.image.load('UI/repeat.png')
    _repeat = Image(_repeat,35,40,104,90)
    _repeat.resize()
    _repeatcopy = pygame.image.load('UI/repeat.png')
    _repeatcopy = Image(_repeatcopy, 35, 40, 104, 90)
    _repeatcopy.resize()
    _scrollbar = pygame.image.load('UI/scrollbar.png')
    _scrollbar = Image(_scrollbar,10,2,43,778)
    _scrollbar.resize()
    _scrollbar.resize(_scrollbar.w,_scrollbar.h - 21)
    _scrollball = pygame.image.load('UI/scrollball.png')
    _scrollball = Image(_scrollball,35,17,74,44)
    _scrollball.resize()
    State._songbar = pygame.image.load('UI/song.png')
    State._songbar = Image(State._songbar,28,28,1097,38)
    State._songbar.resize()
    State._songbar.resize(State._songbar.w,29)
    State._listbar = pygame.image.load('UI/song.png')
    State._listbar = Image(State._listbar,28,28,1097,38)
    State._listbar.resize()
    State._listbar.resize(370,29)
    _sliderbar = pygame.image.load('UI/sliderbar.png')
    _sliderbar = Image(_sliderbar,27,28,1856,30)
    _sliderbar.resize()
    _sliderbar.resize(_sliderbar.w - 20,_sliderbar.h)
    _sliderball = pygame.image.load('UI/sliderball.png')
    _sliderball = Image(_sliderball,15,15,58,58)
    _sliderball.resize()
    _songname = pygame.image.load('UI/songname.png')
    _songname = Image(_songname,0,0,900,32)
    _songname.resize()
    _songname.resize(_songname.w + 85,_songname.h)
    _mov = pygame.image.load('UI/movbutton.png')
    _mov = Image(_mov,36,22,100,83)
    _mov.resize()
    _mov.resize(_mov.w + 5,_mov.h)
    _verde = pygame.image.load('UI/greenbutton.png')
    _verde = Image(_verde,36,22,100,83)
    _verde.resize()
    on = True
    f = []
    text = ''
    allsongsButton = Button(470, -5,0,_mov, 0, 0, 'white', 'All Songs',(20,28))
    pauseButton = Button(960, 616, 0, _pause)
    playButton = Button(960, 616, 0, _play)
    nextButton = Button(1060, 616, 0,_next)
    previousButton = Button(860,616,0,_previous)
    repeatButton = Button(1160, 616, 0,_repeat)
    shuffleButton = Button(760, 616, 0,_shuffle)
    newplaylistButton = Button(-10, -5,0,_verde,0,0, 'white', 'new',(38,27))
    deleteButton = Button(65, -5,0,_verde,0,0, 'white', 'delete',(31,27))
    renamelistButton = Button(140, -5,0,_verde,0,0, 'white', 'rename',(24,27))
    addButton = Button(215, -5,0,_verde,0,0, 'white', 'add',(38,27))
    removeButton = Button(290, -5,0,_verde,0,0, 'white', 'remove',(24,27))
    time = Slider(10, 560, _sliderbar,_sliderball)
    volume = Slider(220, 599,_sliderbar,_sliderball, 300,_sliderbar.h)
    location = ''
    with open('location.txt','r') as loc:
        location = loc.read()
        os.chdir(location)
    location = os.getcwd()
    print(location)
    for (dirpath, dirnames, filenames) in os.walk(location):
        f.extend(filenames)
    i = 0
    for song in f:
        if song.find('.mp3') != -1:
            b = Button(470, 59,i,State._songbar, 0, 30, 'black', song,(20,24))
            State.songbuttons.append(b)
            i = i + 1
    songView = ScrollView(1225, 20, 12, len(State.songbuttons),_scrollbar,_scrollball, 1280 - 450 - 15)
    playlistView = ScrollView(385, 20,  12, 19,_scrollbar,_scrollball,450)

    def drawWindow():
        window.blit(_background,(0,0))
        # pygame.draw.rect(window, (105, 105, 105), (0, 0, 450, 560))  # playlist
        # pygame.draw.rect(window, (105, 105, 105), (460, 0, 1280 - 450 - 10, 560))  # songlist
        #pygame.draw.rect(window, (105, 105, 105), (0, 570, 1280, 720 - 10 - 570))  # controls
        if client.offline:
            window.blit(_nonet,(1152,22))
        else:
            window.blit(_net,(1152,22))
        window.blit(_songname.img, (20,640))
        if State.currentSong != '':
            name = cutText(State.currentSong,_songname.w)
        else:
            name = ''
        text1 = font.render(f"{name}", 1, colors['black'])
        window.blit(text1, (45,665))
        text2 = font.render('Volume', 1, colors['white'])
        window.blit(text2, (148, 612))
        if not State.allsongs:
            font1 = pygame.font.SysFont('berlinsansfb', 40)
            text3 = font1.render(State.playlists[State.playlistIndex].button.textname,1,colors['white'])
            w,h = font1.size(State.playlists[State.playlistIndex].button.textname)
            window.blit(text3, (920 - int(w/2), 15))
        songView.draw(window)
        playlistView.draw(window)
        if State.allsongs:
            for i in range(0, len(State.songbuttons)):
                if songView.list[i]:
                    State.songbuttons[i].update(i - songView.value)
                    State.songbuttons[i].draw(window)
        else:
            for i in range(0, len(State.playlists[State.playlistIndex].songs)):
                if songView.list[i]:
                    State.playlists[State.playlistIndex].songs[i].update(i - songView.value)
                    State.playlists[State.playlistIndex].songs[i].draw(window)

        for i in range(0, len(State.playlists)):
            if playlistView.list[i]:
                State.playlists[i].button.update(i - playlistView.value)
                State.playlists[i].button.draw(window)

        repeatButton.draw(window)
        if State.repeat > 0:
            pixels = pygame.PixelArray(_repeat.img)
            pixels.replace((20,255,25,255),(60,185,185,220),0.405)
            del pixels
            if State.repeat == 1:
                font1 = pygame.font.SysFont('berlinsansfb', 22)
                text3 = font1.render('1', 1, colors['white'])
                window.blit(text3, (1245, 678))
            else:
                font1 = pygame.font.SysFont('berlinsansfb', 25)
                text3 = font1.render('∞', 1, colors['white'])
                window.blit(text3, (1237, 676))
        else:
            repeatButton.img.img = _repeatcopy.img.copy()
        if State.shuffle > 0:
            pixels = pygame.PixelArray(_shuffle.img)
            pixels.replace((20, 255, 25, 255), (60, 185, 185, 220), 0.405)
            del pixels
        else:
            shuffleButton.img.img = _shufflecopy.img.copy()

        removeButton.draw(window)
        addButton.draw(window)
        renamelistButton.draw(window)
        if not State.paused:
            pauseButton.draw(window)
        else:
            playButton.draw(window)
        allsongsButton.draw(window)
        nextButton.draw(window)
        previousButton.draw(window)
        shuffleButton.draw(window)
        newplaylistButton.draw(window)
        deleteButton.draw(window)
        volume.draw(window)
        time.draw(window)
        pygame.display.update()

    while on:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                on = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                length = len(State.songbuttons)
                lista = State.songbuttons
                if not State.allsongs:
                    length = len(State.playlists[State.playlistIndex].songs)
                    lista = State.playlists[State.playlistIndex].songs
                for i in range(0, length):
                    if songView.list[i] == True and lista[i].isMouseOn():
                        selectSong(time, i)
                        State.happened = True
                        volume.setVolume()
                for i in range(0, len(State.playlists)):
                    if State.playlists[i].button.isMouseOn() and playlistView.list[i] == True:
                        if not State.toadd:
                            State.allsongs = False
                            State.happened = True
                            songView.reset(12, len(State.playlists[i].songs))
                            songView.setPosCircle(songView.y)
                            State.playlistIndex = i
                            State.switched = True
                        else:
                            for b in State.playlists[i].songs:
                                if b.name == State.currentSong:
                                    State.toadd = False
                                    break
                            if State.toadd:
                                State.happened = True
                                State.playlists[i].songs.append(Button(470, 59, len(State.playlists[i].songs) + 1,State._songbar,0,0,'black',State.currentSong,(20,24)))
                            State.toadd = False

                if addButton.isMouseOn():
                    add()
                if removeButton.isMouseOn():
                    remove(songView,time)
                    State.happened = True
                if allsongsButton.isMouseOn():
                    allsongs(songView)
                if newplaylistButton.isMouseOn():
                    newplaylist()
                    State.happened = True
                if deleteButton.isMouseOn():
                    deleteplaylist(songView,time)
                    State.happened = True
                if pauseButton.isMouseOn() or playButton.isMouseOn():
                    pause(time)
                    State.happened = True
                if repeatButton.isMouseOn():
                    repeat()
                    State.happened = True
                if renamelistButton.isMouseOn():
                    renamelplaylist()
                if shuffleButton.isMouseOn():
                    shuffle()
                    State.happened = True
                if previousButton.isMouseOn():
                    previous()
                    time.setPosCircle(time.x + time.imgbar.x)
                    time.setTime()
                    State.happened = True
                if nextButton.isMouseOn():
                    next()
                    time.setPosCircle(time.x + time.imgbar.x)
                    time.setTime()
                    State.happened = True
            if pygame.mouse.get_pressed()[0] == 1:
                mouseX, mouseY = pygame.mouse.get_pos()
                if volume.isMouseOnRect():
                    volume.setPosCircle(mouseX)
                    volume.setVolume()
                if time.isMouseOnRect() and State.index != -1:
                    time.setPosCircle(mouseX)
                    time.setTime()
                if songView.isMouseOnBar():
                    songView.setPosCircle(mouseY)
                    songView.update()
                if playlistView.isMouseOnBar() and playlistView.rows < playlistView.total:
                    playlistView.setPosCircle(mouseY)
                    playlistView.update()
            if event.type == pygame.KEYDOWN:
                if State.renamelist:
                    if event.key == pygame.K_RETURN:
                        State.renamelist = False
                        State.happened = True
                        State.playlists[State.playlistIndex].button.name = text
                        text = ''
                        break
                    elif event.unicode == u"\u0008":
                        text = text[:-1]
                    else:
                        text += event.unicode
                    State.playlists[State.playlistIndex].button.textname = text
                    #State.playlists[State.playlistIndex].button.name = text
        if pygame.mixer_music.get_busy() and State.paused == False and (pygame.mouse.get_pressed()[0] != 1 or (
                time.isMouseOnRect() == False)):
            time.getTime(time)
        if State.index != -1:
            time.name = State.currentSong
        if len(State.playlists) > 0:
            playlistView.update(len(State.playlists))
        drawWindow()
        if State.happened:
            client.send_state()
            State.happened = False
    #client.send_state()
    client.send(client.disconnect)
    pygame.quit()

if __name__ == '__main__':
    # pygame.mixer.pre_init(44100, 16, 2, 4096) #frequency, size, channels, buffersize
    pygame.init()  # turn all of pygame on.
    window_dim = (1280, 720)
    window = pygame.display.set_mode(window_dim)
    window_scale = 1920 / 1280
    pygame.display.set_caption('best music player ever')
    font = pygame.font.SysFont('berlinsansfb', 20)
    main()