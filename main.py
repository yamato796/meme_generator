from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from string import ascii_letters
import textwrap
import os
import random
from os import walk
image_lib = './meme_blank/'
txt_lib = './caption/'
image_filenames = next(walk(image_lib), (None, None, []))[2]
txt_filenames = next(walk(txt_lib), (None, None, []))[2]
if '.DS_Store' in image_filenames:
	image_filenames.remove('.DS_Store')
if '.DS_Store' in txt_filenames:
	txt_filenames.remove('.DS_Store')
#print(image_filenames, txt_filenames)

def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False

def insert_text(font_in='Arial.ttf', size_in=50, img=None, text='', area=[0,-1,0,200], fill='#000000'):
	[img_lw, img_rw, img_uh, img_dh] = area
	print([img_lw, img_rw, img_uh, img_dh])
	# Load custom font
	if img_rw == -1:
		img_rw = img.size[0]
	if img_dh == -1:
		img_dh = img.size[1]
	font = ImageFont.truetype(font=font_in, size=size_in)
	# Create DrawText object
	draw = ImageDraw.Draw(im=img)
	# Define our text
	# Calculate the average length of a single character of our font.
	# Note: this takes into account the specific font and font size.
	avg_char_width = sum(font.getsize(char)[0] for char in ascii_letters) / len(ascii_letters)
	# Translate this average length into a character count
	max_char_count = int((img_rw-img_lw) * .918 / avg_char_width)
	# Create a wrapped text object using scaled character count
	text = textwrap.fill(text=text, width=max_char_count)
	# Add text to the image
	draw.text(xy=((img_rw+img_lw)/2, (img_dh+img_uh)/2), text=text, font=font, fill=fill, anchor='mm')

def cap_func(meme_type=0):
	if meme_type==0 or meme_type==1:
		caption_file = txt_lib+str(meme_type)+'.txt'
		caption = random.choice(open(caption_file).readlines())
	return caption


image_path = image_lib+random.choice(image_filenames)
#image_path = image_lib+ '1_30_w_cat_mind_blown_0_x_430_x.png'

img = Image.open(image_path)
filename_list = os.path.basename(image_path).split('.')[0].split('_')
area = filename_list[-4:]
for i in range(0,len(area)):
	if area[i] == 'x':
		area[i] = -1
	else:
		area[i] = int(area[i])
caption = cap_func(meme_type=int(filename_list[0]))
if is_contains_chinese(caption):
	font = 'PingFang.ttc'
else:
	font = 'Arial.ttf'

if filename_list[2] =='b':
	fill = '#000000'
else:
	fill = '#ffffff'

insert_text(font_in=font, img=img, text=caption, area=area, size_in=int(filename_list[1]), fill=fill)
#insert_text(img=img, text=caption, area=area)
img.show()
 
# Save the edited image
img.save("test.png")