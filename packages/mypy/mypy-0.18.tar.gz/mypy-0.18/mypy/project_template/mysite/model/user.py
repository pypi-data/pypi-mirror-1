#coding:utf-8
from init_db import McModel, Model
from mysite.util.security import challenge_key

class UserApply(Model):
    @classmethod
    def is_actived(cls, email):
        u = cls.get(email = email)
        if u and u.is_active:
            return True

    @classmethod
    def get_ck(cls, email):
        u = cls.get(email=email)
        if u is None:
            u = cls(email=email)
            u.ck = challenge_key()
            u.save()
        return u.ck

    @classmethod
    def change_ck(cls, email):
        cls.where(email=email).update(is_active=1, ck=challenge_key())
    

class UserProfile(McModel):
    pass

class User(McModel):
    pass


if __name__ == "__main__":
    for i in User.where()[:100]:
        print i.id, i.name

#G.email_error = None
#if UserApply.is_actived(email):
#    G.email_error = """该邮箱已注册，若忘记密码，<a href="/auth/reset_password">点此重设</a>"""
