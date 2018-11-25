from django.db.models import F
from django.utils.timezone import localtime, now
from django.forms.models import model_to_dict
from .models import User, Email
import hashlib
import random
import string


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


def validate(email, pwd):

    ret = {
        'success': False
    }

    succ = User.objects.filter(email=email, password=pwd)
    if succ.exists():
        succ = succ[0]
        ret['data'] = {
            'email': succ.email,
            'nick':  succ.nick
        }
        ret['success'] = True
        return ret
    else:
        return ret


def add_count(sha1):

    ret = {
        'success': False
    }

    email = Email.objects.filter(sha1=sha1)

    if not email.exists():
        ret['msg'] = 'not found'
        return ret

    email = email[0]
    email.count += 1
    email.save()
    ret['success'] = True
    return ret


def get_events(created_user, limit):

    ret = {
        'success': False
    }
    try:
        emails = Email.objects.filter(create_user=created_user)[:limit]
    except:
        return ret
    ret['success'] = True

    data = []
    for x in emails:
        data.append(model_to_dict(x))

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

    return ret




