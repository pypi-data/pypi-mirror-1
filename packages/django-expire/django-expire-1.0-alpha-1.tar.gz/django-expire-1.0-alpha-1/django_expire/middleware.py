from django.conf import settings as django_settings
from django_expire import models, signals


MAX_USERS = getattr(django_settings, 'EXPIRE_MAX_USERS', 1)


class ExpireMiddleware(object):
    """
    Middleware to handle limiting the number of sessions a user can have.

    """

    def process_request(self, request):
        """
        Limit the number of sessions a user can have, if appropriate.

        This is a no-op if the request is not for an authenticated user.

        """
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated():
            return
        session = getattr(request, 'session', None)
        if not session:
            return
        settings = {'max_users': MAX_USERS}
        signals.expire_check.send(sender=user, settings=settings)

        logs = models.LoggedSession.objects.filter(user=user, active=True)
        try:
            logs.filter(session_id=session.session_key)[0]
        except IndexError:
            # The current user's session is not recorded in the session logs.
            ip = request.META.get('REMOTE_ADDR')
            models.LoggedSession.objects.create(user=user, ip=ip,
                                                session_id=session.session_key)

        max_users = settings.get('max_users')
        if not max_users:
            return
        other_sessions = logs.exclude(session_id=session.session_key)
        allowed = max_users - 1
        if other_sessions.count() > allowed:
            excessive_sessions = other_sessions[allowed:]
            for log in excessive_sessions:
                session.delete(session_key=log.session_id)
            excessive_sessions.update(active=False)
