#coding:utf-8
from zconf.app.config import CAPTCHA_FONT_PATH
from os.path import join

from zku.dmemcached import McCache
from random import randint
import captchaimage
import Image
import sys
from random import sample
from os import urandom
from base64 import urlsafe_b64encode
from cStringIO import StringIO

class Captcha(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.path = "/captcha/%s"%key

    def gif(self):
        value = self.value
        size_y = 50
        if value:
            image_data = captchaimage.create_image(
                CAPTCHA_FONT_PATH,
                40,
                size_y,
                value
            )
            image = Image.fromstring("L", (len(image_data) / size_y, size_y), image_data)
            o = StringIO()
            image.save(o, "GIF")
            return o.getvalue()
        return ""

mc_captcha = McCache("captcha:%s")

def get_capthca(key):
    value = mc_captcha.get(key)
    return Captcha(key, value)

def check_capthca(key, value):
    if key and value:
        if mc_captcha.get(key)==value:
            return True

def del_captcha(key):
    mc_captcha.delete(key)

def new_captcha():
    value = "0123456789"*6
    value = sample(value, 6)
    value = "".join(value)

    key = urlsafe_b64encode(urandom(12))
    mc_captcha.set(key,value,1200)

    return Captcha(key, value)