# -*- coding: utf-8 -*-
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User

class AuthMiddleware(object):

    def process_request(self, request):
        if request.environ.get('repoze.who.identity') is not None:
            repoze_who_user = None
            identity = request.environ['repoze.who.identity']
            if identity is not None:
                repoze_who_user = identity['repoze.who.userid']
            if repoze_who_user is not None:
                user = User.objects.get(email=repoze_who_user)
                request.user = user
