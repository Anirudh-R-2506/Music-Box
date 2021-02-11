#!usr/local/bin/python3
#import all necessary modules
#argparse version of the script
import os
from pynput import keyboard
import sys
from time import sleep
import argparse
from mutagen import File
from random import shuffle
if os.name == "nt":
    os.environ['PYTHON_VLC_MODULE_PATH'] = "VideoLan\\"
    os.environ['PYTHON_VLC_LIB_PATH'] = "VideoLan\\VLC\\libvlc.dll"
import vlc
from threading import Thread

#declare all vars
global playlist
global played
global mp3_player
global keys
global s_name
global per_folder
global kill_thread

#declare all lambdas
base_name = lambda name : os.path.basename(name)
parse_trailing_space = lambda x : x[:-1] if x[-1] == ' ' else x
kill_thread = 1
keys = []
type_music = ''
played = []
s_name = ''
playlist = []
repeat_var = 0
type_music1 = lambda : type_music

class player:#song player object

    def __init__(self):#init function for song player

        self.instance = vlc.Instance()
        self.player: vlc.MediaPlayer = self.instance.media_player_new()

    def load(self,file):#load given song

        self.player.set_media(self.instance.media_new(file))

    def play_song(self,file):#play given song

        self.load(file)
        self.play_pause()

    def set_pos(self,pos):#set position of song

        self.player.set_time(int(pos)*1000)

    def get_pos(self):#get current position of song

        return self.player.get_time() / 1000

    def forward(self,secs):#forward song

        self.set_pos(int(self.get_pos())+secs)

    def rewind(self,secs):#rewind song

        self.set_pos(int(self.get_pos())-secs)

    def play_pause(self):#pause/play song

        if self.has_media() and self.player.is_playing():
            self.player.pause()
        elif self.has_media() and not self.player.is_playing():
            self.player.play()
        else:
            return

    def play_s(self):#play song

        if self.has_media() and not self.player.is_playing():
            self.player.play()

    def pause_s(self):#pause song
        
        if self.has_media() and self.player.is_playing():
            self.player.pause()

    def stop(self):#stop player

        self.player.stop()

    def has_media(self):#check if player has media

        return self.player.get_media() is not None

    def get_length(self):#get total length of media

        return self.player.get_length() / 1000

    def inc_vol(self):#increase volume

        self.player.audio_set_volume(self.player.audio_get_volume() + 10)

    def dec_vol(self):#decrease volume

        self.player.audio_set_volume(self.player.audio_get_volume() - 10)

    def check_pause(self):#check if media is paused

        return self.player.is_playing()

current = set()

def on_press(key):#on_press function for listener

    global kill_thread
    global mp3_player
    global repeat_var
    global type_music

    comb_next = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.right}
    comb_prev = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.left}
    comb_pause = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.space}
    comb_inc = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.up}
    comb_dec = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.down}
    comb_shuff = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('\x13')}
    comb_plus = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('=')}
    comb_minus = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('\x1f')}
    comb_rep = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('\x12')}
    comb_quit = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('\x11')}
    if kill_thread:
        if key == keyboard.Key.media_play_pause:#listen for play/pause key      
            try:
                mp3_player.play_pause()
            except:
                pass
            if os.name == "posix":
                os.system('killall iTunes')
        if key in comb_next:#listen for next song keys
            current.add(key)
            if all(k in current for k in comb_next) and type_music == "dir":
                try:               
                    play_next()
                except:
                    pass
        if key in comb_quit:#listen for quit keys
            current.add(key)
            if all(k in current for k in comb_quit):
                kill_thread = 0
                mp3_player.stop()                
        if key in comb_prev:#listen for previous song keys
            current.add(key)
            if all(k in current for k in comb_prev) and type_music == "dir":
                try:
                    play_prev()
                except:
                    pass
        if key in comb_pause:#listen for pause/play keys
            current.add(key)
            if all(k in current for k in comb_pause):
                try:
                    mp3_player.play_pause()
                except:
                    pass
        if key in comb_shuff:#listen for shuffle keys
            current.add(key)
            if all(k in current for k in comb_shuff) and type_music == "dir":
                try:
                    shuffle(playlist)
                except:
                    pass
        if key in comb_inc:#listen for volume increase keys
            current.add(key)
            if all(k in current for k in comb_inc):
                try:
                    mp3_player.inc_vol()
                except:
                    pass
        if key in comb_dec:#listen for volume decrease keys
            current.add(key)
            if all(k in current for k in comb_dec):
                try:
                    mp3_player.dec_vol()
                except:
                    pass
        if key in comb_rep:#listen for repeat keys
            current.add(key)
            if all(k in current for k in comb_rep) and type_music == "single":                
                try:
                    repeat_var = 1
                except:
                    pass
        if key in comb_plus:#listen for seek song keys
            current.add(key)
            if all(k in current for k in comb_plus):
                try:
                    mp3_player.forward(3)               
                except:
                    pass
        if key in comb_minus:#listen for rewind song keys
            current.add(key)
            if all(k in current for k in comb_minus):
                try:
                    mp3_player.rewind(3)                 
                except:
                    pass


def menu_dir(name):#print key to use and song data for folder player

    if 1:
        m1 = """

PLAY NEXT SONG                        -> PRESS CTRL+ALT+RIGHT ARROW
PLAY PREVIOUS SONG                    -> PRESS CTRL+ALT+LEFT ARROW
PAUSE CURRENT SONG                    -> PRESS CTRL+ALT+SPACE
PLAY CURRENT SONG                     -> PRESS CTRL+ALT+SPACE
SHUFFLE PLAYLIST                      -> PRESS CTRL+ALT+S
INCREASE VOLUME                       -> PRESS CTRL+ALT+UP ARROW
DECREASE VOLUME                       -> PRESS CTRL+ALT+DOWN ARROW
FORWARD CURRENT SONG BY 3 SECONDS     -> PRESS CTRL+ALT+PLUS
REWIND CURRENT SONG BY 3 SECONDS      -> PRESS CTRL+ALT+MINUS
QUIT                                  -> PRESS CTRL+ALT+Q

        """
        if name:
            m1 += '\n\n\n\n[-] NOW PLAYING '+base_name(name)+'\n\n'
        #meta_data = File(name)   
        if 0:            
            m1 += '[-] ALBUM '+meta_data['TALB'][-1] +'\n\n' if meta_data['TALB'][-1] else ''
            m1 += '[-] ARTIST '+meta_data['TPE3'][-1] +'\n\n' if meta_data['TPE3'][-1] else ''
            m1 += '[-] FEAT '+meta_data['TPE1'][-1] +'\n\n' if meta_data['TPE1'][-1] else ''
            m1 += '[-] LYRICIST '+meta_data['TOLY'][-1] +'\n\n' if meta_data['TOLY'][-1] else ''
        return m1

def single(name):#print key to use and song data for single track

    if 1:
        m1 = """

PAUSE CURRENT SONG                    -> PRESS CTRL+ALT+ENTER
PLAY CURRENT SONG                     -> PRESS CTRL+ALT+ENTER
INCREASE VOLUME                       -> PRESS CTRL+ALT+UP ARROW
DECREASE VOLUME                       -> PRESS CTRL+ALT+DOWN ARROW
FORWARD CURRENT SONG BY 3 SECONDS     -> PRESS CTRL+ALT+PLUS
REWIND CURRENT SONG BY 3 SECONDS      -> PRESS CTRL+ALT+MINUS
PLAY CURRENT SONG IN REPEAT           -> PRESS CTRL+ALT+R
QUIT                                  -> PRESS CTRL+ALT+Q

        """
        if name:
            m1 += '\n\n\n\n[-] NOW PLAYING '+base_name(name)+'\n\n'
        #meta_data = File(name)
        if 0:
            m1 += '[-] ALBUM '+meta_data['TALB'][-1] +'\n\n' if meta_data['TALB'][-1] else ''
            m1 += '[-] ARTIST '+meta_data['TPE3'][-1] +'\n\n' if meta_data['TPE3'][-1] else ''
            m1 += '[-] FEAT '+meta_data['TPE1'][-1] +'\n\n' if meta_data['TPE1'][-1] else ''
            m1 += '[-] LYRICIST '+meta_data['TOLY'][-1] +'\n\n' if meta_data['TOLY'][-1] else ''
        return m1
    
def play_next():#play next song

    global type_music
    global kill_thread
    global s_name
    global repeat_var

    if not playlist and type_music == "dir":
        kill_thread = 0
        mp3_player.stop()
        return
    if type_music == "dir":
        print('played')
        played.append(playlist.pop(0))
        mp3_player.play_song(played[-1])
        if os.name == "nt":
            os.system('cls')
        else:
            os.system('clear')
        print(menu_dir(played[-1]))
    elif type_music == "single":
        mp3_player.play_song(s_name)
        if os.name == "nt":
            os.system('cls')
        else:
            os.system('clear')
        print(single(s_name))

def play_prev():#play previous song

    playlist.insert(0,played.pop(-1))
    mp3_player.play_song(played[-1])
    if os.name == "nt":
        os.system('cls')
    else:
        os.system('clear')
    if 1:
        print(menu_dir(played[-1]))

def on_release(key):#on_release function for keylistener
    
    try:
        current.remove(key)
    except KeyError:
        pass

def main1():#listener function for keys from keyboard

    global kill_thread
    while kill_thread:
        with keyboard.Listener(on_press=on_press,on_release=on_release) as listener:
                listener.join()

def not_play():#check if media is playing

    global mp3_player
    sleep(5)
    return not mp3_player.has_media()


def main2():#autoplay function for folder player

    global kill_thread

    play_next()
    sleep(0.5)
    while kill_thread:
        if playlist:   
            if mp3_player.has_media():
                if round(mp3_player.get_pos(),0) != round(mp3_player.get_length(),0):
                    continue    
            if not_play() or round(mp3_player.get_pos(),0) == round(mp3_player.get_length(),0):
                print('played next')
                play_next()
        else:
            break   

def main4():#autoplay function for single track player

    global kill_thread
    global repeat_var

    play_next()
    sleep(0.5)
    while kill_thread:
        if mp3_player.has_media():
            if round(mp3_player.get_pos(),0) != round(mp3_player.get_length(),0):
                continue
            elif repeat_var:
                mp3_player.set_pos(0)
            else:
                kill_thread = 0
        if not kill_thread:
            return
        if repeat_var:
            try:
                mp3_player.set_pos(0)
                continue
            except:                
                if os.name == "nt":
                    os.system('cls')
                else:
                    os.system('clear')
                pri = '[-] SONG HAS BEEN MOVED TO DIFFERENT PATH'
                print(pri)
                kill_thread = 0
                break            
        break

def dir_music(folder,choice,shuff):#driver function for playing all songs from a folder

    global mp3_player
    global type_music
    global playlist
    global played
    global kill_thread
    global s_name
    global repeat_var

    try:
        mp3_player = player()
    except:
        return
    playlist = get_songs(folder,choice)
    if not playlist:
        return 0
    if shuff:
        shuffle(playlist)
    t2 = Thread(target = main2)
    t2.start()#thread to keep autopay and manual control running side by side
    sleep(1)
    while 1:#keep checking for kill_thread var
        if not kill_thread:
            playlist = []
            if os.name == "nt":
                os.system('cls')
            else:
                os.system('clear')
            return 1

def single_music():#driver function for playing a single song

    global mp3_player
    global type_music
    global playlist
    global played
    global kill_thread
    global s_name
    global repeat_var

    try:
        mp3_player = player()
    except:
        return
    t2 = Thread(target = main4)
    t2.start()#thread to keep autopay and manual control running side by side
    sleep(1)
    while 1:#keep checking for kill_thread var
        if not kill_thread:
            if os.name == "nt":
                os.system('cls')
            else:
                os.system('clear')
            return

def get_songs(dirNames,choice):
    allFiles = []
    for dirName in dirNames:        
        listOfFile = os.listdir(dirName)        
        for entry in listOfFile:
            fullPath = os.path.join(dirName, entry)
            if os.path.isdir(fullPath) and choice:
                allFiles = allFiles + get_songs([fullPath],1)
            else:
                a = fullPath
                if a[-3:] == "mp3" or a[-3:] == "wav" or a[-3:] == "ogg" or a[-4:] == "flac" or a[-3:] == "m4a" and '._' not in a:
                    allFiles.append(fullPath)
    return allFiles

if __name__ == "__main__":

    helptext='Play songs from the terminal using VLC\n'
    my_parser = argparse.ArgumentParser(prog='music',
                                        formatter_class=argparse.RawTextHelpFormatter,
                                        description=helptext,
                                        fromfile_prefix_chars='@')
    my_parser.version = 'version 1.0'
    my_parser.add_argument('-f','--folder',
                            type=str,
                            metavar='path',
                            nargs='*',
                            action='store',
                            help='Play all songs from one or many folders(Enter paths seperated by spaces if many and enclose path with " if name contains spaces)')
    my_parser.add_argument('-t','--track',
                            type=str,                            
                            action='store',
                            help='Play a track')
    my_parser.add_argument('-i','--subfolder',
                            action='store_true',
                            help='Include songs from sub folder. Can be used only with -f')
    my_parser.add_argument('-s','--shuffle',
                            action='store_true',
                            help='Shuffle songs when including from folder. Can be used only with -f')
    my_parser.add_argument('-v','--version',
                            action='version',
                            help='Displays the version of the program')
    if len(sys.argv)==1:
        my_parser.print_help(sys.stderr)
        sys.exit(1)
    args = my_parser.parse_args()
    if not args.folder:
        args.folder = [os.getcwd()]
    if args.folder and args.track:
        print('Play from either folder or track')
        sys.exit()
    elif args.folder or args.track:
        c = 1
    elif not args.folder and args.subfolder:
        print('Use -i only with -f option')
        sys.exit()
    elif not args.folder and args.shuffle:
        print('Use -s only with -f option')
        sys.exit()
    else:
        print('Enter an arguement')
        sys.exit()
    if args.track:
        if not os.path.isfile(args.track):
            print('Track does not exist')
            sys.exit()
        else:
            c = 1
    elif args.folder:
        for a in args.folder:
            if not os.path.isdir(a):
                print('Folder '+a+' does not exist')
                sys.exit()
        c = 1

    if c:
        t1 = Thread(target = main1)
        t1.setDaemon = True
        t1.start()#thread for key listening
        if args.folder:
            kill_thread = 1
            args.folder = [parse_trailing_space(a) for a in args.folder]
            type_music = 'dir'
            if args.subfolder:
                dir_music(args.folder,1,args.shuffle)
            else:
                dir_music(args.folder,0,args.shuffle)
        if args.track:
            kill_thread = 1
            type_music = 'single'
            s_name = args.track
            single_music()
        if os.name != 'nt':#scrap all threads
            os.system('killall Python')
        else:#scrap all threads
            os.system('taskkill /F /IM python.exe /T')
