#! /usr/bin/env python
#coding=utf-8
import re
EMAIL_VALID = re.compile(r"^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$")

def email_valid(email):
    return EMAIL_VALID.match(email)


WHITE_SPACE = "\r\n \t"
