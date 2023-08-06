from django.dispatch import Signal


expire_check = Signal(providing_args=['settings'])
"""
A signal which provides a way for changing the settings used to test for
expiration of a user's sessions.

The ``sender`` argument will be the user for whom this expiration test is for.

The ``settings`` argument is a dictionary passed to all listeners which can
be modified if required. 

"""


def superuser_handler(sender, settings, **kwargs):
    """
    An session expiration handler which allows super-users an unlimited number
    of sessions.

    """
    if sender.is_superuser:
        settings['max_users'] = 0
