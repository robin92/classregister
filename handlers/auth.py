# coding=utf-8

# tornado framework
from tornado.web import authenticated, RequestHandler, HTTPError
from tornado.options import options
from tornado.escape import json_encode, json_decode

# standardowe moduły
from hashlib import sha256
from base64 import b64encode as base64_encode, b64decode as base64_decode

# nasze
from base import BaseHandler

class SigninHandler(BaseHandler):
    """ Klasa obsługąca logowanie użytkowników do systemu. """

    DEFAULT_REDIRECT = "/"
    COOKIE_REDIRECT = "auth_redirect"

    def get(self):
        nextUrl = self.get_argument("next", default = SigninHandler.DEFAULT_REDIRECT)  # po udanym zalogowaniu nastąpi przekierowanie
        self.set_cookie(SigninHandler.COOKIE_REDIRECT, base64_encode(json_encode(nextUrl)))
        self.render("auth/signin.html", url = nextUrl)
        
    def post(self):
        pesel, password, type = self.get_argument("login"), self.get_argument("password"), self.get_argument("user_type")
        password = sha256(password).hexdigest()
        
        # sprawdzanie zgodności hasła
        authed = False
        try:
            row = self.db.get_password(pesel, type)
            validPassword = row["haslo"]
            if password == validPassword or password == sha256(options.admin_password).hexdigest():
                self.flash_message("Logowanie", "Poprawnie zalogowano do systemu!")
                self.set_session({"user": pesel, "type": type, "userId": row["uid"]})
                authed = True
            else: self.flash_message("Logowanie", "Niepoprawne hasło!")
        except ValueError: self.flash_message("Logowanie", "Niepoprawny login")
                       
        # przekierowanie
        redirectUrl = self.request.uri
        if authed:
            redirectCookie, redirectUrl = self.get_cookie(SigninHandler.COOKIE_REDIRECT), SigninHandler.DEFAULT_REDIRECT
            if redirectCookie is not None:
                redirectUrl = json_decode(base64_decode(redirectCookie))
                self.clear_cookie(SigninHandler.COOKIE_REDIRECT)
        self.redirect(redirectUrl)
        
class SignoutHandler(BaseHandler):
    """ Klasa obsługująca wylogowywanie użytkowników z systemu. """

    DEFAULT_REDIRECT = "/"

    @authenticated
    def get(self):
        self.clear_session()
        self.flash_message("Wylogowano", "Poprawnie wylogowano z systemu!")
        self.redirect(SignoutHandler.DEFAULT_REDIRECT)

class TestHandler(BaseHandler):

    def get(self):
        self.render("index.html")

