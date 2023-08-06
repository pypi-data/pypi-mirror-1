from desire.django.apps.eui.views.base import DesireView
import desire.command
from dm.exceptions import KforgeCommandError
import random

class AuthenticateView(DesireView):

    def __init__(self, **kwds):
        super(AuthenticateView, self).__init__(**kwds)
        self.isAuthenticateFail = False

    def setMinorNavigationItems(self):
        self.minorNavigation = [
        ]
        if self.session:
            self.minorNavigation.append(
                {'title': 'Welcome',      'url': '/help/'},
            )
            self.minorNavigation.append(
                {'title': 'Log out',      'url': '/logout/'},
            )
        else:
            self.minorNavigation.append(
                {'title': 'Log in',       'url': '/login/'},
            )
            if self.canCreatePerson():
                self.minorNavigation.append(
                    {'title': 'Register',     'url': '/persons/create/'},
                )

    def canAccess(self):
        return True

    def authenticate(self):
        if self.session:
            return True
        params = self.request.POST.copy()
        name = params['name']
        password = params['password']
        command = desire.command.PersonAuthenticate(name, password)
        try:
            command.execute()
        except KforgeCommandError, inst:
            msg = "Login authentication failure for person name '%s'." % name
            self.logger.warn(msg)
        else:
            self.startSession(command.person)

    def setContext(self):
        super(AuthenticateView, self).setContext()
        self.setAuthenticationContext()
        self.context.update({
            'canCreatePerson': self.canCreatePerson(),
            'isAuthenticateFail': self.isAuthenticateFail,
        })

    def setAuthenticationContext(self):
        if self.request.POST:
            params = self.request.POST.copy()
            self.context.update({
                'name': params.get('name', ''),
                'password': params.get('password', ''),
            })


class LoginView(AuthenticateView):

    templatePath = 'login'
    minorNavigationItem = '/login/'

    def login(self, returnPath=''):
        if self.request.POST:
            self.authenticate()
            params = self.request.POST.copy()
            returnPath = params.get('returnPath', '')
            if returnPath:
                self.returnPath = returnPath
            if self.session:
                if returnPath:
                    self.setRedirect(returnPath)
            else:
                self.isAuthenticateFail = True
        elif returnPath:
            self.returnPath = returnPath
        return self.getResponse()


class LogoutView(AuthenticateView):

    templatePath = 'logout'
    minorNavigationItem = '/logout/'

    def logout(self, redirectPath=''):
        self.redirectPath = redirectPath
        self.stopSession()
        return self.getResponse()


def login(request, returnPath=''):
    return LoginView(request=request).login(returnPath)

def logout(request, redirect=''):
    return LogoutView(request=request).logout(redirect)

