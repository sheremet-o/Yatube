from django.urls import reverse
from http import HTTPStatus
from django.test import TestCase, Client


class StaticPagesViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author_page_accessible_by_name(self):
        '''Проверка доступности адреса about:author.'''
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech_page_accessible_by_name(self):
        '''Проверка доступности адреса about:tech.'''
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_templates(self):
        '''URL адреса используют верные шаблоны.'''
        template_urls_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in template_urls_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
