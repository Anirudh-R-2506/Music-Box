#!usr/local/bin/python3
#import all necessary modules
import os
try:
    import vlc
except:
    print('\n[-] PLEASE INSTALL VLC MEDIA PLAYER IN ORDER TO RUN THIS PROGRAM')
import shutil
from pynput import keyboard
from colorama import init
from termcolor import colored
from time import sleep
from random import shuffle
from bs4 import BeautifulSoup
from requests import get
from threading import Thread

#declare all vars
global playlist
global played
global mp3_player
global keys
global s_name
global per_folder
global kill_thread
global progress

#declare all lambdas
base_name = lambda name : os.path.basename(name)
parse_trailing_space = lambda x : x[:-1] if x[-1] == ' ' else x
init()

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
                if a[-3:] == "mp3" or a[-3:] == "wav" or a[-3:] == "ogg" or a[-4:] == "flac" or a[-3:] == "m4a" and a[0:2] != '._':
                    allFiles.append(fullPath)
    return allFiles
kill_thread = 1
progress = 0
keys = []
type_music = ''
per_folder = "songs/my_playlist"
if not os.path.isdir(os.getcwd()+'/'+per_folder):#create personal playlist folder if it does'nt exist
    #os.system('mkdir songs && mkdir songs/my_playlist')
    os.mkdir("songs")
    os.mkdir(per_folder)
played = []
s_name = ''
playlist = []
repeat_var = 0
type_music1 = lambda : type_music

class down_songs:#object to download songs

    def __init__(self,name,path):#init function for downloading songs

        self.name = name
        self.path = path

    def search(self):#search for the song in youtube

        URL = 'https://www.google.com/search?source=hp&ei=DMZHX8SiFreJ4-EP7rW_-Ao&q='+self.name+'+site%3Ayoutube.com&oq='+self.name+'+site%3Atamilrockers.ws&gs_lcp=CgZwc3ktYWIQAzoOCAAQ6gIQtAIQmgEQ5QI6AggAOgIILjoICAAQsQMQgwE6BQguEJMCOggILhCxAxCDAToLCC4QsQMQgwEQkwI6BQguELEDOgUIABCxAzoICC4QsQMQkwI6BggAEBYQHlCFGVixUGDJUmgBcAB4AIABggGIAccPkgEEMjYuMZgBAKABAaoBB2d3cy13aXqwAQY&sclient=psy-ab&ved=0ahUKEwjE2OjtzrvrAhW3xDgGHe7aD68Q4dUDCAY&uact=5'
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
        headers = {"user-agent" : USER_AGENT}
        print()
        pri = colored('[-] LOCATING YOUR SONG','green',attrs=['bold'])
        print(pri)
        resp = get(URL, headers=headers)
        soup = BeautifulSoup(resp.content, "html.parser")
        results = []
        for g in soup.find_all('div', class_='g'):
            anchors = g.find_all('a')
            descript = g.find_all('h3')
            if anchors:
                link = anchors[0]['href']
                desc = descript[0].text
                low_name = self.name.lower().split(' ')
                if not [a for a in low_name if a in desc.lower().split(' ')]:
                    continue
                item = {
                    "link": link,
                }
                results.append(item)
        if not results:
            print()
            pri = colored('[-] COULD NOT FIND YOUR SONG. MAKE SURE YOU USE THE SAME WORDS AS IT APPEARS IN THE OFFICIAL RELEASE','red',attrs=['bold'])
            print(pri)
            return 0
        return results[0]['link'].split('?v=')[-1]

    def get_link(self,suffix):#get link for downloading file

        url = 'https://www.yt-download.org/api/button/mp3/'+suffix
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
        headers = {"user-agent" : USER_AGENT}
        print()
        pri = colored('[-] PREPARING FOR DOWNLOAD','green',attrs=['bold'])
        print(pri)
        resp = get(url, headers=headers)
        soup = BeautifulSoup(resp.content, "html.parser")
        link = soup.find_all('a')[0]['href']
        return link

    def download(self,link):#download file from link

        print()
        pri = colored('[-] BE CALM, SMILE :) AND RELAX. YOUR SONG IS DOWNLOADING','green',attrs=['bold'])
        print(pri)
        r = get(link,allow_redirects=True)
        if open(self.path+self.name.lower()+'.mp3','wb').write(r.content):
            return 1
        return 0

class player:#song player object

    def __init__(self):#init function for song player

        os.environ["VLC_VERBOSE"] = "0"
        self.instance = vlc.Instance("--audio-filter=visual")#headphone
        self.instance.log_unset()
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

def convert(seconds): 
    seconds = seconds % (24 * 3600) 
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    if not hour:
        return "%02d:%02d" % (minutes, seconds) 
    return "%d:%02d:%02d" % (hour, minutes, seconds)

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    if not total:return
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    sec = convert(iteration)
    tot = convert(total)
    if tot == "23:59:59" or sec  == "23:59:59":return
    print(f'\r{prefix} |{bar}| {sec}/{tot}', end = printEnd)
    if iteration == total: 
        print()

current = set()

def on_press(key):#on_press function for listener

    global kill_thread
    global mp3_player
    global repeat_var
    global type_music

    comb_ctrl = {keyboard.Key.ctrl,keyboard.Key.ctrl_l,keyboard.Key.ctrl_r}
    comb_alt = {keyboard.Key.alt,keyboard.Key.alt_l,keyboard.Key.alt_gr}
    comb_next = {keyboard.Key.right}
    comb_prev = {keyboard.Key.left}
    comb_pause = {keyboard.Key.space}
    comb_inc = {keyboard.Key.up}
    comb_dec = {keyboard.Key.down}
    comb_shuff = {keyboard.KeyCode.from_char('\x13'),keyboard.KeyCode.from_char('ś')}
    comb_plus = {keyboard.KeyCode.from_char('='),keyboard.KeyCode.from_char('+')}
    comb_minus = {keyboard.KeyCode.from_char('\x1f'),keyboard.KeyCode.from_char('-')}
    comb_add = {keyboard.KeyCode.from_char('\x01'),keyboard.KeyCode.from_char('ā')}
    comb_rep = {keyboard.KeyCode.from_char('\x12'),keyboard.KeyCode.from_char('r̥')}
    comb_quit = {keyboard.KeyCode.from_char('\x11'),keyboard.KeyCode.from_char('æ')}
    comb_master = [comb_add,comb_dec,comb_inc,comb_shuff,comb_quit,comb_plus,comb_rep,comb_pause,comb_minus,comb_prev,comb_alt,comb_ctrl,comb_next]
    
    try:
        if kill_thread and mp3_player.has_media():        
            if key == keyboard.Key.media_play_pause:#listen for play/pause key      
                try:
                    mp3_player.play_pause()
                except Exception as e:
                    pri = colored('[-] COULD NOT PAUSE/PLAY SONG ','red',attrs=['bold'])
                    print('\n')
                    print(pri)
                if os.name == "posix":
                    os.system('killall iTunes')
            if len(current) >= 2 and any(k in current for k in comb_ctrl) and any(k in current for k in comb_alt) and [b for a in comb_master for b in a if b == key]:            
                if key in comb_next:#listen for next song keyscurrent.add(key)
                    if type_music == "dir":
                        try:               
                            play_next()
                        except Exception as e:
                            pri = colored('[-] COULD NOT PLAY NEXT SONG ','red',attrs=['bold'])
                            print('\n')
                            print(pri)
                if key in comb_quit:#listen for quit keys
                    if 1:
                        kill_thread = 0
                        mp3_player.stop()                
                if key in comb_prev:#listen for previous song keys
                    if type_music == "dir":
                        try:
                            play_prev()
                        except Exception as e:
                            pri = colored('[-] COULD NOT PLAY PREVIOUS SONG ','red',attrs=['bold'])
                            print('\n')
                            print(pri)
                if key in comb_pause:#listen for pause/play keys
                    if 1:
                        try:
                            mp3_player.play_pause()
                        except Exception as e:
                            pri = colored('[-] COULD NOT PAUSE/PLAY SONG ','red',attrs=['bold'])
                            print('\n')
                            print(pri)
                if key in comb_shuff:#listen for shuffle keys
                    if type_music == "dir":
                        try:
                            shuffle(playlist)
                        except Exception as e:
                            pri = colored('[-] COULD NOT SHUFFLE PLAYLIST ','red',attrs=['bold'])
                            print('\n')
                            print(pri)
                if key in comb_inc:#listen for volume increase keys                
                    if 1:
                        try:
                            mp3_player.inc_vol()
                        except Exception as e:
                            pri = colored('[-] COULD NOT INCREASE VOLUME ','red',attrs=['bold'])
                            print('\n')
                            print(pri)
                if key in comb_dec:#listen for volume decrease keys                
                    if 1:
                        try:
                            mp3_player.dec_vol()
                        except Exception as e:
                            pri = colored('[-] COULD NOT DECREASE VOLUME ','red',attrs=['bold'])
                            print('\n')
                            print(pri)
                if key in comb_add:#listen for add to playlist keys
                    if 1:
                        try:
                            add_to()                    
                        except Exception as e:
                            print(e)
                            pri = colored('[-] COULD NOT ADD CURRENT SONG TO PERSONAL PLAYLIST ','red',attrs=['bold'])
                            print('\n')
                            print(pri)
                if key in comb_rep:#listen for repeat keys
                    if type_music == "single":                
                        try:
                            repeat_var = 1
                            pri = colored('[-] PLAYING CURRENT SONG ON REPEAT ','green',attrs=['bold'])
                            print('\n')
                            print(pri)
                        except Exception as e:
                            pri = colored('[-] COULD NOT REPEAT CURRENT SONG ','red',attrs=['bold'])
                            print('\n')
                            print(pri)
                if key in comb_plus:#listen for seek song keys
                    if 1:
                        try:
                            mp3_player.forward(3)               
                        except Exception as e:
                            print(e)
                            pri = colored('[-] COULD NOT SEEK SONG ','red',attrs=['bold'])
                            print('\n')
                            print(pri)
                if key in comb_minus:#listen for rewind song keys
                    if 1:
                        try:
                            mp3_player.rewind(3)                 
                        except Exception as e:
                            print(e)
                            pri = colored('[-] COULD NOT REWIND SONG ','red',attrs=['bold'])
                            print('\n')
                            print(pri)
            else:
                current.add(key)
    except:
        pass


def menu_dir(name):#print key to use and song data for folder player

    if 1:
        m1 = """

                                KEY TO USE THE MUSIC PLAYER

                PLAY NEXT SONG                        -> PRESS CTRL+ALT+RIGHT ARROW
                PLAY PREVIOUS SONG                    -> PRESS CTRL+ALT+LEFT ARROW
                PAUSE CURRENT SONG                    -> PRESS CTRL+ALT+SPACE
                PLAY CURRENT SONG                     -> PRESS CTRL+ALT+SPACE
                SHUFFLE PLAYLIST                      -> PRESS CTRL+ALT+S
                INCREASE VOLUME                       -> PRESS CTRL+ALT+UP ARROW
                DECREASE VOLUME                       -> PRESS CTRL+ALT+DOWN ARROW
                FORWARD CURRENT SONG BY 3 SECONDS     -> PRESS CTRL+ALT+PLUS
                REWIND CURRENT SONG BY 3 SECONDS      -> PRESS CTRL+ALT+MINUS
                ADD CURRENT SONG TO PERSONAL PLAYLIST -> PRESS CTRL+ALT+A
                QUIT TO MAIN MENU                     -> PRESS CTRL+ALT+Q

        """
        if name:
            m1 += '\n\n\n\n[-] NOW PLAYING '+base_name(name)+'\n\n'        
        return colored(m1,'green',attrs=['bold'])

def single(name):#print key to use and song data for single track

    if 1:
        m1 = """

                                KEY TO USE THE MUSIC PLAYER

                PAUSE CURRENT SONG                    -> PRESS CTRL+ALT+ENTER
                PLAY CURRENT SONG                     -> PRESS CTRL+ALT+ENTER
                INCREASE VOLUME                       -> PRESS CTRL+ALT+UP ARROW
                DECREASE VOLUME                       -> PRESS CTRL+ALT+DOWN ARROW
                FORWARD CURRENT SONG BY 3 SECONDS     -> PRESS CTRL+ALT+PLUS
                REWIND CURRENT SONG BY 3 SECONDS      -> PRESS CTRL+ALT+MINUS
                PLAY CURRENT SONG IN REPEAT           -> PRESS CTRL+ALT+R OR
                ADD CURRENT SONG TO PERSONAL PLAYLIST -> PRESS CTRL+ALT+A OR
                QUIT TO MAIN MENU                     -> PRESS CTRL+ALT+Q OR

        """
        if name:
            m1 += '\n\n\n\n[-] NOW PLAYING '+base_name(name)+'\n\n'        
        return colored(m1,'green',attrs=['bold'])
    
def play_next():#play next song

    global type_music
    global kill_thread
    global s_name
    global repeat_var
    global progress

    if not playlist and type_music == "dir":
        kill_thread = 0
        mp3_player.stop()
        return
    if type_music == "dir":
        played.append(playlist.pop(0))
        mp3_player.play_song(played[-1])
        if os.name == "nt":
            os.system('cls')
        else:
            os.system('clear')
        print(menu_dir(played[-1]))
        sleep(0.5)
        #printProgressBar(0, mp3_player.get_length(), prefix = '⏪⏯ ⏩️', suffix = '', length = 84)
        progress = 1
    elif type_music == "single":
        mp3_player.play_song(s_name)
        if os.name == "nt":
            os.system('cls')
        else:
            os.system('clear')
        print(single(s_name))
        sleep(0.5)
        #printProgressBar(0, mp3_player.get_length(), prefix = '⏪⏯ ⏩️', suffix = '', length = 84)
        progress = 1

def play_prev():#play previous song

    global progress

    playlist.insert(0,played.pop(-1))
    mp3_player.play_song(played[-1])
    if os.name == "nt":
        os.system('cls')
    else:
        os.system('clear')
    if 1:
        print(menu_dir(played[-1]))
        sleep(0.5)
        #printProgressBar(0, mp3_player.get_length(), prefix = '⏪⏯ ⏩️', suffix = '', length = 84)
        progress = 1

def add_to():#add song to personal playlist

    if type_music == "dir" and base_name(played[-1]) not in os.listdir(per_folder):
        shutil.copyfile(played[-1],per_folder+'/'+base_name(played[-1]))
    elif type_music == "single" and base_name(s_name) not in os.listdir(per_folder):
        shutil.copyfile(s_name,per_folder+'/'+base_name(s_name))
    else:
        print()
        pri = colored('[-] SONG ALREADY EXISTS IN PLAYLIST','red',attrs=['bold'])
        print(pri)
        return
    pri = colored('[-] ADDED CURRENT SONG TO PERSONAL PLAYLIST ','green',attrs=['bold'])
    print('\n')
    print(pri)

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
    while kill_thread or mp3_player.has_media():        
        if playlist:                                                 
            if mp3_player.has_media():                                                
                if round(mp3_player.get_pos(),0) != round(mp3_player.get_length(),0):
                    printProgressBar(mp3_player.get_pos(), mp3_player.get_length(), prefix = '⏪⏯ ⏩️', suffix = '', length = 84)
                    continue                                            
            if not_play() or round(mp3_player.get_pos(),0) == round(mp3_player.get_length(),0):
                play_next()                        
        else:
            while progress:                
                printProgressBar(mp3_player.get_pos(), mp3_player.get_length(), prefix = '⏪⏯ ⏩️', suffix = '', length = 84)
            else:    
                break   

def main4():#autoplay function for single track player

    global kill_thread
    global repeat_var

    play_next()
    while kill_thread:
        if mp3_player.has_media():
            if round(mp3_player.get_pos(),0) != round(mp3_player.get_length(),0):
                printProgressBar(mp3_player.get_pos(), mp3_player.get_length(), prefix = '⏪⏯ ⏩️', suffix = '', length = 84)
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
                print()
                pri = colored('[-] SONG HAS BEEN MOVED TO DIFFERENT PATH','red',attrs=['bold'])
                print(pri)
                kill_thread = 0
                break            
        break

def dir_music(folder,choice):#driver function for playing all songs from a folder

    global mp3_player
    global type_music
    global playlist
    global played
    global per_folder
    global kill_thread
    global s_name
    global repeat_var
    global progress

    mp3_player = player()
    playlist = get_songs(folder,choice)
    if not playlist:
        return 0
    t2 = Thread(target = main2)
    t2.setDaemon = True
    t2.start()#thread to keep autopay and manual control running side by side
    while 1:#keep checking for kill_thread var                
        if not kill_thread:
            playlist = []
            progress = 0            
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
    global per_folder
    global kill_thread
    global s_name
    global repeat_var
    global progress

    mp3_player = player()
    t2 = Thread(target = main4)
    t2.setDaemon = True
    t2.start()#thread to keep autopay and manual control running side by side
    sleep(1)
    while 1:#keep checking for kill_thread var
        if not kill_thread:
            progress = 0
            if os.name == "nt":
                os.system('cls')
            else:
                os.system('clear')
            return

def add_per(folder):#add current song to playlist

    while 1:
        try:
            print()
            inp = colored('[-] ENTER FULL PATH TO SONG(S) SEPERATED BY COMMAS IF MANY ')
            filez = input(inp)
        except:
            print()
            pri = colored('[-] INVALID PATH')
            print(pri)
            continue
        file_list = filez.split(',')
        check = [a for a in file_list if a[-3:] == "mp3" or a[-3:] == "wav" or a[-3:] == "ogg" or a[-4:] == "flac" and os.path.isfile(a)]
        if not check:
            for a in check:
                print()
                pri = colored('[-] INVALID SONG '+a,'red',attrs=['bold'])
                print(pri)
            continue
        break
    for a in file_list:
        shutil.copyfile(a,per_folder+'/'+base_name(a))
        print()
        pri = colored('[-] ADDED '+base_name(a)+' TO PERSONAL PLAYLIST','green',attrs=['bold'])
        print(pri)

def list_per(folder):#list all tracks in personal playlist

    print()
    m1 = "[-] TRACKS IN PLAYLIST\n\n"
    count = 0
    list_songs = os.listdir(folder)
    for a in list_songs:
        count += 1
        if a[-3:] == "mp3" or a[-3:] == "wav" or a[-3:] == "ogg" or a[-4:] == "flac":
            m1 += str(count)+') '+a + '\n'
    if m1 != "[-] TRACKS IN PLAYLIST\n\n":
        pri = colored(m1,'green',attrs=['bold'])
    else:
        return 0
    print(pri)
    print('\n\n\n')
    return 1

def make_archive(source, destination):#make .zip file in desired location

    base = base_name(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = base_name(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s'%(name,format), destination)

def export_per(folder):#export personal playlist as .zip file in desired location

    while 1:
        try:
            print()
            inp = colored('[-] ENTER PATH TO EXPORT ','green',attrs=['bold'])
            folder2 = input(inp)
            if not os.path.isdir(folder):
                print('[-] PATH DOES NOT EXIST')
                continue
            pri2 = ''
            break
        except EOFError:
            print()
            pri = colored('[-] INVALID CHOICE','red',attrs=['bold'])
            print(pri)
    if os.name == "nt":
        folder2 += '\\playlist.zip'
    else:
        folder2 += '/playlist.zip'
    try:
        make_archive(folder,folder2)
    except:
        pri2=colored('[-] COULD NOT EXPORT PLAYLIST ','red',attrs=['bold'])
        return
    if pri2:
        if os.name == "nt":
            os.system('cls')
        else:
            os.system('clear')
        print()
        print(pri2)
        return
    pri2 = colored('[-] EXPORTED PLAYLIST AS '+folder2,'green',attrs=['bold'])
    if os.name == "nt":
        os.system('cls')
    else:
        os.system('clear')
    print()
    print(pri2)

def open_f(folder):#open personal playlist to view and edit

    if os.name == "nt":
        if os.path.isdir(folder):
            os.system('explorer '+folder)
        else:
            print('\n')
            pri = colored("[-] FOLDER DOES NOT EXIST",'red',attrs=['bold'])
            print(pri)
    elif os.name == "posix":
        if os.path.isdir(folder):
            os.system('open '+folder)
        else:
            print('\n')
            pri = colored("[-] FOLDER DOES NOT EXIST",'red',attrs=['bold'])
            print(pri)
    else:
        if os.path.isdir(folder):
            os.system('xdg-open '+folder)
        else:
            print('\n')
            pri = colored("[-] FOLDER DOES NOT EXIST",'red',attrs=['bold'])
            print(pri)
    if os.name == "nt":
        os.system('cls')
    else:
        os.system('clear')

def main_menu():#driver function
    
    global mp3_player
    global type_music
    global playlist
    global played
    global per_folder
    global kill_thread
    global s_name
    global repeat_var

    t1 = Thread(target = main1)
    t1.setDaemon = True
    t1.start()#thread for key listening
    if os.name == "nt":
        os.system('cls')
    else:
        os.system('clear')
    fancy_text = """
    

 /$$      /$$ /$$   /$$  /$$$$$$  /$$$$$$  /$$$$$$        /$$$$$$$   /$$$$$$  /$$   /$$
| $$$    /$$$| $$  | $$ /$$__  $$|_  $$_/ /$$__  $$      | $$__  $$ /$$__  $$| $$  / $$
| $$$$  /$$$$| $$  | $$| $$  \__/  | $$  | $$  \__/      | $$  \ $$| $$  \ $$|  $$/ $$/
| $$ $$/$$ $$| $$  | $$|  $$$$$$   | $$  | $$            | $$$$$$$ | $$  | $$ \  $$$$/ 
| $$  $$$| $$| $$  | $$ \____  $$  | $$  | $$            | $$__  $$| $$  | $$  >$$  $$ 
| $$\  $ | $$| $$  | $$ /$$  \ $$  | $$  | $$    $$      | $$  \ $$| $$  | $$ /$$/\  $$
| $$ \/  | $$|  $$$$$$/|  $$$$$$/ /$$$$$$|  $$$$$$/      | $$$$$$$/|  $$$$$$/| $$  \ $$
|__/     |__/ \______/  \______/ |______/ \______/       |_______/  \______/ |__/  |__/                                                                                                                                 
                                          v1.0

                A COMPUTER SCIENCE PROJECT BY ANIRUDH R OF CLASS 12 E


"""
    menu = """
[-] SELECT YOUR CHOICE

1) PLAY A SONG
2) PLAY SONGS FROM A FOLDER
3) PLAY SONGS FROM MULTIPLE FOLDERS
4) PLAY PERSONAL PLAYLIST
5) LIST SONGS IN PERSONAL PLAYLIST
6) EXPORT PERSONAL PLAYLIST AS .zip FILE
7) OPEN PERSONAL PLAYLIST TO VIEW
8) ADD SONG(S) TO PERSONAL PLAYLIST
9) DOWNLOAD SONGS TO PERSONAL PLAYLIST
10) QUIT

"""
    menu = colored(fancy_text + menu,'green',attrs=['bold'])
    while 1:
        try:
            print()
            print('\r'*100)
            choice = str(input(menu))
            choice = choice[-2:]
            if choice.isnumeric() :
                choice = int(choice)
            else:
                choice = int(choice[-1])
            if choice not in (1,2,3,4,5,6,7,8,9,10):
                print()
                pri = colored('[-] INVALID CHOICE','red',attrs=['bold'])
                print(pri)
                continue    
        except:
            pri = colored('[-] INVALID CHOICE','red',attrs=['bold'])
            print(pri)
            continue
        if os.name == "nt":
            os.system('cls')
        else:
            os.system('clear')
        if choice == 10:
            print()
            pri = colored('[-] THANK YOU FOR USING MUSIC BOX :)','green',attrs=['bold'])
            print(pri)
            return
        elif choice == 1:
            type_music = "single"
            kill_thread = 1
            while 1:
                try:
                    print()
                    inp = colored('[-] ENTER FULL PATH TO SONG ','green',attrs=['bold'])
                    s_name = input(inp)
                    s_name = parse_trailing_space(s_name)
                    if not os.path.isfile(s_name):
                        print()
                        pri = colored('[-] FILE DOES NOT EXIST','red',attrs=['bold'])
                        print(pri)
                        continue
                    break
                except:
                    print()
                    pri = colored('[-] INVALID CHOICE','red',attrs=['bold'])
                    print(pri)
            single_music()
        elif choice == 2:
            type_music = "dir"
            kill_thread = 1
            while 1:
                try:
                    print()
                    inp = colored('[-] ENTER FULL PATH TO DIRECTORY CONTAINING SONGS ','green',attrs=['bold'])
                    folder = input(inp)
                    folder = parse_trailing_space(folder)
                    if not os.path.isdir(folder):
                        print()
                        pri = colored('[-] PATH DOES NOT EXIST','red',attrs=['bold'])
                        print(pri)
                        continue
                    break
                except:
                    print()
                    pri = colored('[-] INVALID CHOICE','red',attrs=['bold'])
                    print(pri)
            while 1:
                try:
                    inp = colored('[-] DO YOU WANT TO INCLUDE SONGS FROM SUBFOLDERS(Y/N)? ','green',attrs=['bold'])
                    print()
                    multi = input(inp)
                    if multi.lower() not in 'yn':
                        print()
                        pri = colored('[-] INVALID CHOICE ','red',attrs=['bold'])
                        print(pri)
                        continue
                    multi = 1 if multi.lower() == 'y' else 0
                    break
                except:
                    print()
                    pri = colored('[-] INVALID CHOICE ','red',attrs=['bold'])
                    print(pri)
                    continue
            if not dir_music([folder],multi):
                print()
                pri = colored('[-] NO SONGS IN FOLDER','red',attrs=['bold'])
                print(pri)
        elif choice == 3:
            type_music = "dir"
            kill_thread = 1
            while 1:
                try:
                    print()
                    inp = colored('[-] ENTER FULL PATH TO DIRECTORIES SEPERATED BY COMMAS ','green',attrs=['bold'])
                    folder = input(inp).split(',')
                    folder = [parse_trailing_space(a) for a in folder]
                    for a in folder:
                        if not os.path.isdir(a):
                            print()
                            pri = colored('[-] PATH'+a+'DOES NOT EXIST','red',attrs=['bold'])
                            print(pri)
                            continue
                    break
                except:
                    print()
                    pri = colored('[-] INVALID CHOICE','red',attrs=['bold'])
                    print(pri)
            while 1:
                try:
                    inp = colored('[-] DO YOU WANT TO INCLUDE SONGS FROM SUBFOLDERS(Y/N)? ','green',attrs=['bold'])
                    print()
                    multi = input(inp)
                    if multi.lower() not in 'yn':
                        print()
                        pri = colored('[-] INVALID CHOICE ','red',attrs=['bold'])
                        print(pri)
                        continue
                    multi = 1 if multi.lower() == 'y' else 0
                    break
                except:
                    print()
                    pri = colored('[-] INVALID CHOICE ','red',attrs=['bold'])
                    print(pri)
                    continue
            if not dir_music(folder,multi):
                print()
                pri = colored('[-] NO SONGS IN FOLDERS','red',attrs=['bold'])
                print(pri)
        elif choice == 4:
            type_music = "dir"
            kill_thread = 1
            if list_per(per_folder):
                dir_music([per_folder],0)
            else:
                pri = colored('[-] NO SONG(S) IN PERSONAL PLAYLIST','red',attrs=['bold'])
                print(pri)
        elif choice == 5:
            list_per(per_folder)
        elif choice == 6:
            export_per(per_folder)
        elif choice == 7:
            open_f(per_folder)
        elif choice == 8:
            add_per(per_folder)
        elif choice == 9:
            looper = 1
            while looper:
                try:
                    print()
                    inp = colored('[-] ENTER FULL NAME OF THE SONG ','green',attrs=['bold'])
                    name = input(inp)
                    if os.path.isfile(per_folder+'/'+name.lower()+'.mp3'):
                        if os.name == "nt":
                            os.system('cls')
                        else:
                            os.system('clear')
                        print()
                        pri = colored('[-] SONG ALREADY EXISTS IN YOUR PLAYLIST')
                        print(pri)
                        looper = 0
                        continue
                    break
                except:
                    print()
                    pri = colored('[-] INVALID CHOICE','red',attrs=['bold'])
                    print(pri)
            if looper:
                downloader = down_songs(name,per_folder+'/')
                search = downloader.search()
                if search:
                    if downloader.download(downloader.get_link(search)):
                        if os.name == "nt":
                            os.system('cls')
                        else:
                            os.system('clear')
                        print()
                        pri = colored('[-] DOWNLOADED SONG TO YOUR PLAYLIST','green',attrs=['bold'])
                        print(pri)
                    else:
                        if os.name == "nt":
                            os.system('cls')
                        else:
                            os.system('clear')
                        print()
                        pri = colored('[-] COULD NOT DOWNLOAD SONG TO YOUR PLAYLIST','red',attrs=['bold'])
                        print(pri)

if __name__ == "__main__":
    main_menu()    
    if os.name != 'nt':#scrap all threads
        os.system('killall Python > /dev/null')
    else:#scrap all threads
        os.system('taskkill /F /IM python.exe /T')