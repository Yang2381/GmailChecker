from django.shortcuts import render

from django.http import HttpResponse
from datetime import datetime
import time
import random
import re
import json

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# Create your views here.
from . import db_manager
from mail_auth.auth import Auth

@csrf_exempt
def index(request):
    for key, value in request.session.items():
        print('{} => {}'.format(key, value))
    return HttpResponse("")


@csrf_exempt
@require_http_methods(["POST"])
def login(request):

    token = request.POST.get('token', None)
    if token:
        result = db_manager.validate_with_token(token)
        if result['success']:
            request.session['email'] = result['data']['email']
            request.session['nick'] = result['data']['nick']
            ret = {
                'success': True,
                'nick': result['data']['nick'],
                'token': result['data']['token']
            }
            return HttpResponse(json.dumps(ret))

    email = request.POST.get('email', None)
    password = request.POST.get('password', None)
    if not email or not password:
        return create_failure_response('Email or Password field empty')

    result = db_manager.validate(email, password)

    if not result['success']:
        return create_failure_response('Login failed')

    request.session['email'] = email
    request.session['nick'] = result['data']['nick']

    ret = {
        'success': True,
        'nick': result['data']['nick'],
        'token': result['data']['token']
    }

    return HttpResponse(json.dumps(ret))


@csrf_exempt
@require_http_methods(["POST"])
def create_user(request):

    email = request.POST.get('email', None)
    password = request.POST.get('password', None)
    nick = request.POST.get('nick', 'User')

    if not email or not password:
        return create_failure_response('Email or Password field empty')

    result = db_manager.create_user(email, password, nick)

    if not result['success']:
        return create_failure_response(result['msg'])

    return create_simple_success_response()


@csrf_exempt
@require_http_methods(["POST"])
def create_pair(request):

    auth = Auth(request)
    if not auth.is_login:
        return create_failure_response('Not logged in')

    src = request.POST.get('src', None)
    tar = request.POST.get('tar', None)
    detail = request.POST.get('detail', None)
    email_id = request.POST.get('email_id', None)

    if not src or not tar:
        return create_failure_response('Email field empty')

    result = db_manager.add_record(auth.email, src, tar, detail, email_id)

    if not result['success']:
        return create_failure_response(result['msg'])

    ret = {
        'success': True,
        'img_url': '{}/get/{}.png'.format(settings.SITE_URL, result['sha1'])
    }

    return HttpResponse(json.dumps(ret))


@csrf_exempt
@require_http_methods(["GET"])
def get_events(request):

    auth = Auth(request)
    if not auth.is_login:
        return create_failure_response('Not logged in')

    limit = int(request.GET.get('limit', 10))
    if limit > 20:
        limit = 20

    result = db_manager.get_events(auth.email, limit)
    if not result['success']:
        return create_failure_response(result['msg'])

    return create_simple_success_response(json.dumps(result['data']))


def add_count(request, sha1):

    result = db_manager.add_count(sha1)

    return HttpResponse("")


def create_simple_success_response(msg=None):
    ret = {
        'success': True
    }
    if msg:
        ret['msg'] = msg
    return HttpResponse(json.dumps(ret))


def create_failure_response(msg):
    ret = {
        'success': False,
        'msg': msg
    }
    return HttpResponse(json.dumps(ret))



