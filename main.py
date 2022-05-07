from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from string import ascii_letters
import textwrap
import os
import random
import tweepy
import json
import cv2
import pygame
import subprocess
import threading
import time
import argparse
from os import walk
from os import path
from Quartz import CGDisplayBounds
from Quartz import CGMainDisplayID

parser = argparse.ArgumentParser()
parser.add_argument("-t", help='twitter function toggle', action="store_true")
parser.add_argument("-p", help='printer function toggle', action="store_true")
parser.add_argument("-testimage", help='filename for testing image', type=str)
args = parser.parse_args()

def screen_size():
    mainMonitor = CGDisplayBounds(CGMainDisplayID())
    return (mainMonitor.size.width, mainMonitor.size.height) 

image_lib = './meme_blank/'
txt_lib = './caption/'
output = './output/'
twitter_credential = './config/twitter.json'
image_filenames = next(walk(image_lib), (None, None, []))[2]
txt_filenames = next(walk(txt_lib), (None, None, []))[2]
output_filenames = next(walk(output), (None, None, []))[2]
if '.DS_Store' in image_filenames:
    image_filenames.remove('.DS_Store')
if '.DS_Store' in txt_filenames:
    txt_filenames.remove('.DS_Store')
if '.DS_Store' in output_filenames:
    output_filenames.remove('.DS_Store')
#print(image_filenames, txt_filenames)


class twitter_action():
    
    def __init__(self):
        with open(twitter_credential) as jsonfile:
            self.twitter_auth_keys = json.load(jsonfile)

    def get_auth(self):
        self.auth = tweepy.OAuthHandler(self.twitter_auth_keys['consumer_key'],
                                       self.twitter_auth_keys['consumer_secret'])
        self.auth.set_access_token(self.twitter_auth_keys['access_token'],
                                  self.twitter_auth_keys['access_token_secret'])
        self.api = tweepy.API(self.auth)

    def upload_image(self,tweet=None,img=None):
        self.get_auth()
        media = self.api.media_upload(img)
        post_result = self.api.update_status(status=tweet, media_ids=[media.media_id])

class meme_process():

    def __init__(self):
        self.generate_imge_text_pair()
        self.retry_count = 10

    def generate_imge_text_pair(self):
        if args.testimage:
            #self.path = image_lib+'6_60_w_traincrashbus_420_850_220_380_0_450_620_900.png'
            self.path = args.testimage
        else:
            self.path = image_lib+random.choice(image_filenames)
        self.meme_type = int(os.path.basename(self.path)[0])
        self.img = Image.open(self.path)
        self.filename_list = os.path.basename(self.path).split('.')[0].split('_')
        self.size_in = int(self.filename_list[1])
        self.res = self.cap_func(self.meme_type)


    def is_contains_chinese(self,strs):
        for _char in strs:
            if '\u4e00' <= _char <= '\u9fa5':
                return True
        return False

    def check_duplicate(self,name,line):
        tmp = f"{name}_{line}.png"
        if tmp in output_filenames:
            print(f"{tmp} Duplicated ")
            return False
        else:
            return True

    def insert_text(self, font_in='Arial.ttf', size_in=50, img=None, text='', area=[0,-1,0,200], fill='#000000'):
        if img == None:
            img=self.img

        [img_lw, img_rw, img_uh, img_dh] = area


        if fill =='#ffffff':
            stroke_fill = '#000000'
        else:
            stroke_fill = '#ffffff'

        if img_rw == -1:
            img_rw = img.size[0]
        if img_dh == -1:
            img_dh = img.size[1]

        font = ImageFont.truetype(font=font_in, size=size_in)
        draw = ImageDraw.Draw(im=img)

        if font_in == 'PingFang.ttc':
            avg_char_width = sum(font.getsize(char)[0] for char in ascii_letters) / len(ascii_letters)
            max_char_count = int((img_rw-img_lw) * .5 / avg_char_width)
        else:
            avg_char_width = sum(font.getsize(char)[0] for char in ascii_letters) / len(ascii_letters)
            max_char_count = int((img_rw-img_lw) * .918 / avg_char_width)

        text = textwrap.fill(text=text, width=max_char_count)
        draw.text(xy=((img_rw+img_lw)/2, (img_dh+img_uh)/2), text=text, font=font, fill=fill, anchor='mm',stroke_width=2, stroke_fill=stroke_fill)

    def cap_func(self,meme_type=0):
        #if meme_type==0 or meme_type==1:
        caption_file = txt_lib+str(meme_type)+'.txt'
        temp = open(caption_file).readlines()
        pool = len(temp)
        self.s = random.randint(0,pool-1)
        caption = temp[self.s]
        return caption, self.s

    def avoid_duplicate(self):
        while 1:
            self.generate_imge_text_pair()
            if self.check_duplicate(self.filename_list[3],self.res[1]):
                break
            elif self.retry_count ==0:
                break
            else:
                self.retry_count = self.retry_count -1

    def draw_text_on_img(self):
        if self.meme_type == 3 or self.meme_type == 4:
            area = []
            area.append(self.filename_list[-12:-8])
            area.append(self.filename_list[-8:-4])
            area.append(self.filename_list[-4:])
            cap, s = self.res[0].split('|'), self.res[1]
            for a in range(0,len(area)):
                for i in range(0,len(area[a])):
                    if area[a][i] == 'x':
                        area[a][i] = -1
                    else:
                        area[a][i] = int(area[a][i])
                
                if self.is_contains_chinese(cap[a]):
                    font = 'PingFang.ttc'
                else:
                    font = 'Arial.ttf'

                if self.filename_list[2] =='b':
                    fill = '#000000'
                else:
                    fill = '#ffffff'

                self.insert_text(font_in=font,text=cap[a], area=area[a], size_in=self.size_in, fill=fill)
        elif self.meme_type == 6:
            area = []
            area.append(self.filename_list[-8:-4])
            area.append(self.filename_list[-4:])
            cap, s = self.res[0].split('|'), self.res[1]
            for a in range(0,len(area)):
                for i in range(0,len(area[a])):
                    if area[a][i] == 'x':
                        area[a][i] = -1
                    else:
                        area[a][i] = int(area[a][i])
                
                if self.is_contains_chinese(cap[a]):
                    font = 'PingFang.ttc'
                else:
                    font = 'Arial.ttf'

                if self.filename_list[2] =='b':
                    fill = '#000000'
                else:
                    fill = '#ffffff'

                self.insert_text(font_in=font,text=cap[a], area=area[a], size_in=self.size_in, fill=fill)
        else:
            area = self.filename_list[-4:]
            for i in range(0,len(area)):
                if area[i] == 'x':
                    area[i] = -1
                else:
                    area[i] = int(area[i])
            caption, s = self.res
            if self.is_contains_chinese(caption):
                font = 'PingFang.ttc'
            else:
                font = 'Arial.ttf'

            if self.filename_list[2] =='b':
                fill = '#000000'
            else:
                fill = '#ffffff'

            self.insert_text(font_in=font, text=caption, area=area, size_in=self.size_in, fill=fill)


def py_game_show_image(filename):
    
    screen_resolution = screen_size()
    center_image = True
    image = pygame.image.load(filename)

    screen_w, screen_h = screen_resolution
    image_w, image_h = image.get_size()

    screen_aspect_ratio = screen_w / screen_h
    photo_aspect_ratio = image_w / image_h

    if screen_aspect_ratio < photo_aspect_ratio:  # Width is binding
        new_image_w = screen_w
        new_image_h = int(new_image_w / photo_aspect_ratio)
        image = pygame.transform.scale(image, (new_image_w, new_image_h))
        image_x = 0
        image_y = (screen_h - new_image_h) // 2 if center_image else 0

    elif screen_aspect_ratio > photo_aspect_ratio:  # Height is binding
        new_image_h = screen_h
        new_image_w = int(new_image_h * photo_aspect_ratio)
        image = pygame.transform.scale(image, (new_image_w, new_image_h))
        image_x = (screen_w - new_image_w) // 2 if center_image else 0
        image_y = 0

    else:  # Images have the same aspect ratio
        image = pygame.transform.scale(image, (screen_w, screen_h))
        image_x = 0
        image_y = 0

    gameDisplay.blit(image, (image_x, image_y))

def upload_twitter_check(t_flag=False,filename=None):
    if t_flag:
        if (not filename in output_filenames):
            t = twitter_action()
            print('upload image to twitter')
            #t.upload_image(tweet='#meme #迷因 #memeteller #bonk',img='./test.png')
        else:
            print('image existed on twitter')    

def generate_meme(lock, cnt=10, timer=5, t_flag=False, p_flag=False):
    while 1:

        m = meme_process()
        m.avoid_duplicate()
        m.draw_text_on_img()
        lock.acquire()
        m.img.save("test.png")
        lock.release()
        save_path = output+f"{m.filename_list[3]}_{m.s}.png"
        print('display')
        upload_twitter_check(t_flag, f"{m.filename_list[3]}_{m.s}.png")

        m.img.save(output+f"{m.filename_list[3]}_{m.s}.png")
        if p_flag:
            print("Print meme")
            #os.system("lpr -o media=meme_size test.png")
        time.sleep(timer)
        if cnt<=0:
            break
        cnt = cnt -1


def test_image(t_flag=False):
    m = meme_process()
    m.avoid_duplicate()
    m.draw_text_on_img()
    m.img.show()
    save_path = output+f"{m.filename_list[3]}_{m.s}.png"
    upload_twitter_check(t_flag, f"{m.filename_list[3]}_{m.s}.png")

    m.img.save(output+f"{m.filename_list[3]}_{m.s}.png")


print(f'Twitter toggle: {args.t}')
print(f'Printer toggle: {args.p}')
if args.testimage:
    print(args.testimage)
    test_image(t_flag=args.t)
else:
    pygame.init()
    display_width,display_height = screen_size()
    gameDisplay = pygame.display.set_mode((display_width,display_height))
    black = (0,0,0)
    white = (255,255,255)

    lock = threading.Lock()
    t = threading.Thread(target=generate_meme,args=(lock, 5, 5, args.t, args.p))
    t.start()
    clock = pygame.time.Clock()
    crashed = False
    carImg = pygame.image.load('test.png')
    while not crashed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
        #generate()
        gameDisplay.fill(black)
        if lock.acquire():
            py_game_show_image('test.png')
            lock.release()

            
        pygame.display.update()
        clock.tick(60)

    t.join()
    pygame.quit()
    quit()

