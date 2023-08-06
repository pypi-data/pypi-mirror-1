
from manicscript.jsoncore.decorators import json, login_required
from django.contrib.auth import authenticate, login as manual_login, logout as manual_logout

@json
def profile(request, response):
        # Extract credentials
        response['result'] = 'error'
        response['text'] = 'Unexpected error in accessing profile.'
        if request.user.is_authenticated():
                user = request.user
                response['logged_in'] = True
                response['username'] = user.username
                response['last_name'] = user.last_name
                response['first_name'] = user.first_name
        else:
                response['logged_in'] = False

        # Operation Complete!
        response['result'] = 'ok'
        response['text'] = 'Profile retrieved successfully.'

@json
def login(request, response):
        # Extract credentials
        response['result'] = 'error'
        response['text'] = 'Did not receive credentials.'
        username = request.POST['username']
        password = request.POST['password']

        # Attempt to authenticate user
        user = authenticate(username=username, password=password)
        if user is None:
                response['text'] = 'Invalid login.'
                return
        if not user.is_active:
                response['text'] = 'Account disabled.'
                return

        # Log in user
        response['text'] = 'System failure during user login.'
        manual_login(request, user)

        # Operation Complete!
        response['result'] = 'ok'
        response['text'] = 'User authenticated.'
        return
        
@json
@login_required
def logout(request, response):
        # Log out the user
        response['result'] = 'error'
        response['text'] = 'System failure during user logout.'
        manual_logout(request)

        # Operation Complete!
        response['result'] = 'ok'
        response['text'] = 'User logged out.'
        return
