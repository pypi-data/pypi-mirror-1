from os.path import join,dirname,abspath
from random import randint
import Image

try:
    import captchaimage
    FONT_FILE=join(dirname(abspath(__file__)),"font.ttf")
    def captcha():
        text=str(randint(0,999999)).zfill(6)
        size_y=38
        image_data = captchaimage.create_image(
            FONT_FILE,
            38,
            size_y,
            text
        )
        img = Image.fromstring(
            "L", 
            (len(image_data) // size_y,size_y),
            image_data
        )
        return text,img
except ImportError:
    print "\nWarning: captchaimage not exist, use fake_captchaimage\n"
    from fake_captchaimage import captcha



"""
from random import randint
import captchaimage
import Image
import sys

size_y=38
for i in range(10):
    text=str(randint(1000,9999))
    image_data = captchaimage.create_image(
        "font.ttf",38,size_y,
        text
    )
    print i,text

    image = Image.fromstring(
        "L", (len(image_data) / size_y, size_y), image_data)
    image.save("pics/%s.gif"%i,"GIF") 
except ImportError:
    def captch():
        return 6491,
"""
