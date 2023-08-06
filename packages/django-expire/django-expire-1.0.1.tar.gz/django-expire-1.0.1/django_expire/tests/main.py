from django.contrib.auth.models import User
from django.test.client import Client
from django_expire.models import LoggedSession
from django_expire.utils.module_wrapper import ModuleWrapperTestCase


class ExpireTest(ModuleWrapperTestCase):
    urls = 'django_expire.tests.urls'
    modules = {'middleware': 'django_expire.middleware'}

    def log_in_joe(self, number_of_clients):
        """
        Log in Joe to a number of clients then get the user name for each
        client, returning a list of the responses for each client.

        """
        user = User(username='joe')
        user.set_password('password')
        user.save()

        clients = []
        for i in range(number_of_clients):
            client = Client()
            assert client.login(username='joe', password='password')
            client.get('/')
            clients.append(client)
        
        return [client.get('/').content for client in clients]

    def test_expiry(self):
        self.middleware.MAX_USERS = 1

        user1 = User(username='joe')
        user1.set_password('password')
        user1.save()
        user2 = User(username='jane')
        user2.set_password('password')
        user2.save()
        joe_login_data = {'username': 'joe', 'password': 'password'}
        jane_login_data = {'username': 'jane', 'password': 'password'}

        # Log in Joe.
        assert self.client.login(**joe_login_data)
        response = self.client.get('/')
        self.assertEqual(response.content, 'joe')

        # Log in Jane in a separate client (to check it doesn't inadvertently
        # log out Joe).
        second_client = Client()
        assert second_client.login(**jane_login_data)
        response = second_client.get('/')
        self.assertEqual(response.content, 'jane')
        response = self.client.get('/')
        self.assertEqual(response.content, 'joe')

        # Now log in Joe to the second client, which will invalidate his
        # original session.
        assert second_client.login(**joe_login_data)
        response = second_client.get('/')
        self.assertEqual(response.content, 'joe')
        response = self.client.get('/')
        self.assertEqual(response.content, '')

    def test_max_users(self):
        self.middleware.MAX_USERS = 2

        # Log in Joe to three clients.
        responses = self.log_in_joe(3)

        # Joe should have been logged out of the first session.
        self.assertEqual(responses, ['', 'joe', 'joe'])

    def test_log_limit(self):
        self.middleware.LOG_LIMIT = None
        self.middleware.MAX_USERS = 1
        inactive_sessions = LoggedSession.objects.filter(active=False)

        self.log_in_joe(10)
        self.assertEqual(inactive_sessions.count(), 9)   # 1 still active

        inactive_sessions.delete()
        self.middleware.LOG_LIMIT = 2
        self.log_in_joe(10)
        self.assertEqual(inactive_sessions.count(), 2)

        inactive_sessions.delete()
        self.middleware.LOG_LIMIT = 0
        self.log_in_joe(10)
        self.assertEqual(inactive_sessions.count(), 0)
