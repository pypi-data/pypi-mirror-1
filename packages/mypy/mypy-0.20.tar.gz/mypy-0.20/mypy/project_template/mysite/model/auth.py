#coding:utf-8
from init_db import McModel, Model
from mysite.util.security import get_ck
from hashlib import sha256 as password_hash
from base64 import urlsafe_b64encode
from sendmail import render_email
from struct import pack

class UserEmail(McModel):
    pass

class UserPassword(Model):
    def verify(self, password):
        p = self.password
        return p == hash_password(self.id, password)

class UserApply(Model):
    pass

class User(McModel):
    pass

class UserProfile(McModel):
    pass

def hash_password(id, password):
    return password_hash("%s%s"%(password, pack('L', id))).digest()

def send_apply_email(email, name, id, ck):
    render_email("auth/send_apply_email", email, name, id=id, ck=ck)

def apply(email, password, name):
    id = UserEmail.get_or_create(email=email).id

    password = hash_password(id, password)
    user_password = UserPassword.get(id=id)
    if user_password is None:
        user_password = UserPassword(id=id)
    user_password.password = password
    user_password.save()

    apply = UserApply.get(id)
    if apply is None:
        apply = UserApply(id=id, ck=get_ck())
    apply.name = name
    apply.save()

    ck = urlsafe_b64encode(apply.ck)

    send_apply_email(email, name, id, ck)

    return apply

def is_existed(email):
    e = UserEmail.get(email=email)
    if e:
        return User.mc_get(e.id)

def create_user(id):
    apply = UserApply.get(id)
    if apply:
        user = User(id=id, name=apply.name)
        user.save()
        apply.delete()
        return user

USER_RELATED_BY_ID = (User, UserEmail, UserApply, )

def remove_user_by_email(email):
    UserEmail.begin()
    e = UserEmail.get(email=email)
    if e:
        id = e.id
        for cls in USER_RELATED_BY_ID:
            cls(id=id).delete()
        e.delete()
    UserEmail.commit()




