#coding:utf-8
from os import urandom
from base64 import urlsafe_b64encode, urlsafe_b64decode

def get_b64ck():
    return urlsafe_b64encode(urandom(6))

def get_ck():
    return urandom(6)

def decode_b64ck(key):
    try:
        return  urlsafe_b64decode(key)
    except TypeError:
        pass
