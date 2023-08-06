#coding:utf-8
from mypy.route_render import route_render_func
from mypy.dict_like import Jsdict, StripJsdict
from mysite.model.auth import User, UserApply, UserProfile, UserPassword
from mysite.model import auth
from mysite.util.valid import email_valid
from mysite.util.text import WHITE_SPACE, cnenlen, email2link
from cgi import escape


def apply_error(form):
    email = form.email
    name = form.name
    password = form.password

    error = Jsdict()

    name_len = cnenlen(name)
    if name_len > 8:
        error.name = "名号不要超过8个汉字"
    elif 0 == name_len:
        error.name = "请输入名号"

    password_len = len(password)
    if password_len < 6:
        error.password = "密码最少需要6个字符"
    elif password_len > 60:
        error.password = "密码长度不得超过60个字符"

    if not email:
        error.email = "请输入邮箱"
    elif email_valid(email):
        existed = auth.is_existed(email)
        if existed:
            error.email = """该邮箱已注册,<a href="/auth/reset_password/%s">点此重设密码</a>。"""%escape(email)
    else:
        error.email = "邮箱格式有误，请检查"

    if not error:
        apply = auth.apply(email, password, name)
        auth.send_apply_email(email, name, apply.id, apply.ck)
    return error

@route_render_func
def apply():
    if request.is_post:
        form = StripJsdict(request.form)
        G.error = error = apply_error(form)
        email = form.email
        if not error:
            G.email_link = email2link(email)

@route_render_func
def reg():
    pass

@route_render_func
def login():
    pass

@route_render_func
def reset_password(email=""):
    G.email = email


