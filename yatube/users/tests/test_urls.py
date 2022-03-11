from http import HTTPStatus
from django.test import TestCase, Client


class UsersURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_signup_url_exists_at_desired_location(self):
        '''Страница signup доступна любому пользователю.'''
        response = self.guest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_signup_uses_correct_temolate(self):
        '''Страница signup использует правильный шаблон.'''
        response = self.guest_client.get('/auth/signup/')
        self.assertTemplateUsed(response, 'users/signup.html')
