#coding:utf-8
from mypy.route_render import route_render_func
from mypy.dict_like import Form,StripForm
from mysite.model.user import User,UserApply,UserProfile,UserPassword
from mysite.util.valid import email_valid
from mysite.util.text import WHITE_SPACE,cnenlen,email2link
from cgi import escape

    
def apply_error(form):
    email = form.email
    name = form.name
    password = form.password

    error = Form()
    
    name_len = cnenlen(name)
    if name_len>8:
        error.name = "名号不要超过8个汉字"
    elif 0 == name_len:
        error.name = "请输入名号"
    
    if len(password)<6:
        error.password = "密码最少需要6个字符"
    elif password>=32:
        error.password = "密码长度不得超过31个字符"
    
    if not email:
        error.email = "请输入邮箱"
    elif email_valid(email):
        existed = UserPassword.get(email)
        if existed:
            error.email = """该邮箱已注册,你可以<a href="/auth/reset_password/%s">点此重设密码</a>。"""%escape(existed.email)
    else:
        error.email = "邮箱格式有误，请检查" 
    
    if not error:
        UserApply.sendmail(email)
    
    return error

@route_render_func
def apply():
    if request.is_post:
        form = StripForm(request.form)
        G.error = error = apply_error(form)
        G.email = form.email
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


