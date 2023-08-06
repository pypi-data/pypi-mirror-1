from django.contrib import auth
from django.contrib.auth.models import User
from django.conf import settings

from urlauth.util import load_key, InvalidKey
from urlauth.models import AuthKey
from urlauth.signals import key_processed, key_loaded


class AuthKeyMiddleware(object):
    """
    This middleware can authenticate user with auth key in HTTP request.
    """

    def process_request(self, request):

        key = request.REQUEST.get(settings.URLAUTH_AUTHKEY_NAME)
        
        try:
            key = load_key(key)
        except InvalidKey:
            return

        key_loaded.send(sender=AuthKey, key=key, request=request)

        try:
            user = User.objects.get(pk=key.uid)
        except User.DoesNotExist:
            pass
        else:
            if user.is_active:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth.login(request, user)    

            key_processed.send(sender=AuthKey, key=key, request=request)

        if key.onetime:
            key.delete()
        else:
            request.authkey = key
