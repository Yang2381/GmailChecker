
class Auth:

    def __init__(self, request):
        self.is_login = True if 'email' in request.session else False
        if self.is_login:
            self.email = request.session['email']
            self.nick = request.session['nick']

    def is_login(self):
        return self.is_login
