import Image, ImageDraw
from random import choice, randrange

def get_number():
    return randrange(1,9)

def calc_size(im, ratio):
    rectangle = [(0,0), im.size]
    ratio = (1 - ratio)/2
    h = im.size[1] * ratio
    w = im.size[0] * ratio
    new_ret = [(w,h), (im.size[0] - w, im.size[1] - h)]
    return new_ret

def draw(im, actual_size,  number):
    counter = 1
    width_offset = 2
    d = ImageDraw.Draw(im)
    for i in range(number):
        if i != 4:
            h1 = actual_size[0][1] + 1
            w1 = actual_size[0][0] + counter + width_offset
            h2 = actual_size[1][1] - 1
            w2 = actual_size[0][0] + counter + width_offset
            d.line([(w1,h1), (w2, h2)], fill=(0,0,0))
            counter = counter + 5
        else:
            h1 = actual_size[0][1] + 2
            w1 = actual_size[0][0] + counter + 1
            h2 = actual_size[1][1] - 2
            w2 = actual_size[0][0]
            d.line([(w1,h1), (w2, h2)], fill=(0,0,0))
            counter = counter + 5

def captcha(fp, number):
    """
    Generates number captcha
    argument
    file  - file descriptor for the file
    number - to show as image in range of 1 to 9
    
    """
    if type(number) != 'int' and (number < 0 or number > 9):
        raise AttributeError, 'Number not in range'
    
    im = Image.new("RGB", (55,22), (255,255,255))
    actual_size = calc_size(im, 3.0/4)
    draw(im, actual_size, number)
    im.save(fp, "png")
    return    
