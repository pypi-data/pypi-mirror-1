#coding:utf-8
from init_db import McCache

from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import parseaddr, formataddr
from base64 import encodestring

NOT_SUPPORT_UTF8_DOMAIN = set(['tom.com', 'hotmail.com', 'msn.com', 'yahoo.com'])

def ignore_encode(s, enc):
    return s.decode('utf-8', 'ignore').encode(enc, 'ignore')

import  smtplib
from myconf.config import PREFIX, SMTP, SMTP_USERNAME, SMTP_PASSWORD, SYS_EMAIL_SENDER, SYS_EMAIL_SENDER_NAME

def send_email_imp(
                smtp,
                sender, sender_name,
                recipient, recipient_name,
                subject, body, enc='utf-8',
                format='plain'
            ):

    if not subject:
        return

    at = recipient.find('@')
    if at <= 0:
        return

    domain = recipient[at+1:].strip()
    if domain not in NOT_SUPPORT_UTF8_DOMAIN:
        enc = 'utf-8'
    else:
        enc = "gb18030"

    if enc.lower() != 'utf-8':
        sender_name = ignore_encode(sender_name)
        recipient_name = ignore_encode(recipient_name)
        body = ignore_encode(body)
        subject = ignore_encode(subject, enc)

    msg = MIMEText(body, format, enc)
    msg['Subject'] = Header(subject, enc)

    sender_name = str(Header(sender_name, enc))
    msg['From'] = formataddr((sender_name, sender))

    recipient_name = str(Header(recipient_name, enc))
    msg['To'] = formataddr((recipient_name, recipient))

    smtp.sendmail(sender, recipient, msg.as_string())


from os.path import join
from decorator import decorator
from mypy.byteplay import Code, opmap


TXT_PATH = join(PREFIX, "mysite/txt")

McMailTmp = McCache("MailTmp:%s")

def render_template(uri, **kwds):
    txt = McMailTmp.get(uri)

    if txt is None:
        with open("%s/%s.txt"%(TXT_PATH, uri)) as template:
            txt = template.read()
            McMailTmp.set(uri, txt, 600)

    txt = txt.format(**kwds)
    r = txt.split("\n", 1)
    if len(r) < 2:
        r.append(txt[0])
    return r

def send_email(subject, text, email, name, sender=SYS_EMAIL_SENDER, sender_name=SYS_EMAIL_SENDER_NAME):
    server = smtplib.SMTP(SMTP)
    server.login(SMTP_USERNAME, SMTP_PASSWORD)

    send_email_imp(server, sender, sender_name, email, name, subject, text)

    server.quit()

def render_email(uri, email, name, sender=SYS_EMAIL_SENDER, sender_name=SYS_EMAIL_SENDER_NAME, **kwds):
    if "name" not in kwds:
        kwds['name'] = name

    if "email" not in kwds:
        kwds['email'] = email

    if "sender" not in kwds:
        kwds['sender'] = sender

    if "sender_name" not in kwds:
        kwds['sender_name'] = sender_name

    subject, text = render_template(uri, **kwds)
    send_email(subject, text, email, name, sender, sender_name)
