import string
from random import Random
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


USER_ALLOWED_CHARS = string.letters + string.digits


def create_random_user(username_length=24, allowed_chars=USER_ALLOWED_CHARS):
    """ Create a user with random username and password.
    
    The password will be the same as username.

    Example:

        >>> from django.contrib.auth import authenticate
        >>> user = create_random_user()
        >>> user = authenticate(username=user.username,
        ...                     password=user.username)
        >>> user.is_authenticated()
        True

    """
    username = "".join([Random().choice(allowed_chars)
                            for i in range(username_length)])
    email = "%s@example.com" % username
    user = User.objects.create_user(username, email, username)
    user.save()
    return user 
