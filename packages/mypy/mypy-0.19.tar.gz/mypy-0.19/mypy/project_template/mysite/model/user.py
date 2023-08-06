#coding:utf-8
from init_db import McModel, Model
from mysite.util.security import get_ck

class UserApply(Model):
    @classmethod
    def sendmail(self,email):
        pass

class UserPassword(McModel):
    pass

class UserProfile(McModel):
    pass

class User(McModel):
    pass


