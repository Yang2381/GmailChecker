
from backend_server import db_manager


class Auth:

    def __init__(self, request):

        self.is_login = True if 'email' in request.session else False

        if not self.is_login:
            token = request.POST.get('token', None)
            if token:
                result = db_manager.validate_with_token(token)
                if result['success']:
                    self.email = result['data']['email']
                    self.nick = result['data']['nick']
                    self.is_login = True

        else:
            self.email = request.session['email']
            self.nick = request.session['nick']

    def is_login(self):
        return self.is_login
