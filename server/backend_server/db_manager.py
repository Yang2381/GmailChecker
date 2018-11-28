from django.db.models import F
from django.utils.timezone import localtime, now
from django.forms.models import model_to_dict
from .models import User, Email, ViewEvents
from datetime import datetime, timedelta
from PIL import Image
import hashlib
import random
import string
import sys
import traceback
from django.db import connection


def my_custom_sql(sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    row = cursor.fetchall()
    return row


def get_random_string(N):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))


def create_user(email, pwd, nick):

    ret = {
        'success': False
    }

    user = User.objects.filter(email=email)
    if user.exists():
        ret['msg'] = 'User Already exists'
        return ret

    user = User(email=email, password=pwd, nick=nick)
    user.save()

    ret['success'] = True

    return ret


def validate_with_token(token):

    ret = {
        'success': False
    }

    succ = User.objects.filter(token=token)
    if succ.exists():
        succ = succ[0]
        if succ.token_expire < datetime.today().date():
            return ret
        ret['data'] = {
            'email': succ.email,
            'nick':  succ.nick,
            'token': succ.token,
            'expire': succ.token_expire
        }
        ret['success'] = True
        return ret
    else:
        return ret


def validate(email, pwd):

    ret = {
        'success': False
    }

    succ = User.objects.filter(email=email, password=pwd)
    if succ.exists():
        succ = succ[0]
        new_token = get_random_string(40)
        new_expire = datetime.now() + timedelta(days=7)
        succ.token = new_token
        succ.token_expire = new_expire
        succ.save()
        ret['data'] = {
            'email': succ.email,
            'nick':  succ.nick,
            'token': succ.token,
            'expire': succ.token_expire
        }
        ret['success'] = True
        return ret
    else:
        return ret


def add_count(sha1, client_ip):

    ret = {
        'success': False
    }

    email = Email.objects.filter(sha1=sha1)

    if not email.exists():
        ret['msg'] = 'not found'
        return ret

    email = email[0]
    email_id = email.id

    event = ViewEvents(email_id=email_id, client_ip=client_ip)
    event.save()
    ret['success'] = True

    return ret


def get_events(created_user, limit):

    ret = {
        'success': False
    }
    try:
        emails = Email.objects.filter(create_user=created_user).order_by('-created_at')[:limit]
        email_ids = []
        for e in emails:
            email_ids.append(str(e.id))
        in_str = '(' + ','.join(email_ids) + ')'
        print (in_str)
        emails = my_custom_sql('''
             SELECT id, email_id, cnt, client_ip, tar_email, detail, created_at from gmail_checker.backend_server_email D
             INNER JOIN
             (SELECT email_id, cnt, client_ip FROM gmail_checker.backend_server_viewevents A
             INNER JOIN
                    (
                      SELECT count(0) as cnt, max(id) as gid FROM gmail_checker.backend_server_viewevents WHERE
                          email_id in {}
                          GROUP BY email_id
                    )B
             ON A.id = B.gid)C
             ON D.id = C.email_id
        '''.format(in_str))
    except:
        traceback.print_exc()
        return ret

    ret['success'] = True

    data = []
    for x in emails:
        datum = {
            'email_id': x[1],
            'cnt': x[2],
            'client_ip': x[3],
            'tar_email': x[4],
            'detail': x[5],
            'created_at': x[6].strftime("%Y-%m-%d %H:%M:%S")
        }
        data.append(datum)

    ret['data'] = data

    return ret


def add_record(created_user, src, tar, detail, mail_id=None):

    ret = {
        'success': False
    }

    sha1 = hashlib.sha1(get_random_string(80).encode('utf-8')).hexdigest()

    if Email.objects.filter(sha1=sha1).exists():
        ret['msg'] = 'duplicate record'
        return ret

    email = Email(create_user=created_user, src_email=src, tar_email=tar, sha1=sha1, message_id=mail_id, detail=detail)
    email.save()

    ret['success'] = True
    ret['sha1'] = sha1

    img = Image.new('RGB', (1, 1))
    img.save('backend_server/files/{}.png'.format(sha1))

    return ret




