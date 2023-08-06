#coding:utf-8
from os import urandom
from base64 import urlsafe_b64encode

def challenge_key():
    return urlsafe_b64encode(urandom(6))
