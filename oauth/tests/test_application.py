import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.models import get_access_token_model
from ..models import Application
# Create your tests here.


class ApplicationTestCase(TestCase):
    def setUp(self):
        oauth2_settings._SCOPES = {"read": "ler", "write": "escrever"}
        oauth2_settings.SCOPES = {"read": "ler", "write": "escrever"}
        oauth2_settings._DEFAULT_SCOPES = ['read']
        self.dev_user = User.objects.create_user('dev_user', 'dev@email.com')
        self.test_user = User.objects.create_user('test_user', 'test@email.com')
        self.app1 = Application.objects.create(
            name="meu app",
            description="minha descrição",
            user=self.dev_user,
            scope="read",
            redirect_uris="http://localhost.com http://test.com"
        )
        self.app2 = Application.objects.create(
            name="meu app 2",
            description="minha descrição",
            user=self.dev_user,
            scope="write"
        )
        self.tok1 = get_access_token_model().objects.create(
            user=self.test_user, token="1234567890",
            application=self.app2,
            expires=timezone.now() + datetime.timedelta(days=1),
            scope="read write"
        )

    def test_requested_scopes(self):
        app1_scopes = self.app1.requested_scopes
        app2_scopes = self.app2.requested_scopes
        self.assertEqual(app1_scopes, set(['read']))
        self.assertEqual(app2_scopes, set(['read', 'write']))

    def test_requested_scopes_dict(self):
        app1_scopes = self.app1.requested_scopes_dict
        app2_scopes = self.app2.requested_scopes_dict
        self.assertEquals(app1_scopes, {"read": "ler"})
        self.assertEquals(app2_scopes, {"read": "ler", "write": "escrever"})

    def test_redirect_uris_list(self):
        redirect_uris = self.app1.redirect_uris_list
        self.assertEquals(redirect_uris, ["http://localhost.com", "http://test.com"])

    def test_approved_scopes(self):
        approved_scopes = self.app2.approved_scopes(self.test_user)
        self.assertEqual(approved_scopes, {"read": "ler", "write": "escrever"})

    def test_get_users(self):
        users = self.app2.get_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users.first(), self.test_user)

    def test_scoped_user_id(self):
        scoped1 = Application.get_scoped_user_id(self.app1, self.test_user)
        scoped2 = Application.get_scoped_user_id(self.app1, self.dev_user)
        scoped3 = Application.get_scoped_user_id(self.app2, self.test_user)
        scoped4 = Application.get_scoped_user_id(self.app2, self.dev_user)

        self.assertNotIn(scoped1, [scoped2, scoped3, scoped4])
        self.assertNotIn(scoped2, [scoped3, scoped4])
        self.assertNotIn(scoped3, [scoped4])

        a1, u1 = Application.recover_scoped_user_id(scoped1, True)
        a12, u2 = Application.recover_scoped_user_id(scoped2, True)
        a2, u12 = Application.recover_scoped_user_id(scoped3, True)
        a22, u22 = Application.recover_scoped_user_id(scoped4, True)
        self.assertEqual(u1, u12)
        self.assertEqual(u2, u22)
        self.assertNotEqual(u1, u2)
        self.assertEqual(a1, a12)
        self.assertEqual(a2, a22)
        self.assertNotEqual(a1, a2)
