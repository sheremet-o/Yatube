from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Group, Post
from django.http import HttpResponseNotFound


User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            pk='1',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

# Проверяем общедоступные страницы
    def test_home_url_exists_at_desired_location(self):
        '''Страница / доступна любому пользователю.'''
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_list_url_exists_at_desired_location(self):
        '''Страница /group/<slug>/ доступна любому пользователю.'''
        response = self.guest_client.get(f'/group/{self.group.slug}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url_exists_at_desired_location(self):
        '''Страница /profile/<username>/ доступна любому пользователю.'''
        response = self.guest_client.get(f'/profile/{self.user.username}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail_url_exists_at_desired_location(self):
        '''Страница /posts/<post_id>/ доступна любому пользователю.'''
        response = self.guest_client.get(f'/posts/{self.post.pk}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

# Проверяем доступность страниц для авторизованного пользователя
    def test_create_url_exists_at_desired_location(self):
        '''Страница create доступна авторизованному пользователю.'''
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

# Проверка доступности редактирования поста только для автора
    def test_post_edit_url_exists_at_desired_location(self):
        '''Страница /posts/post_id/edit/ доступна автору поста.'''
        self.user = User.objects.get(username='HasNoName')
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)
        response = self.authorized_client_author.get(
            f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

# Проверка вывода ошибки 404 при переходе на несущестующую страницу
    def test_unexisting_page_url_raises_error(self):
        '''Переход на несуществующую страницу вызывает ошибку 404'''
        response = self.guest_client.get(HttpResponseNotFound())
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

# Проверка вызываемых шаблонов для каждого адреса
    def test_create_url_uses_correct_template(self):
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_post_edit_url_uses_correct_template(self):
        self.user = User.objects.get(username='HasNoName')
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)
        response = self.authorized_client_author.get(
            f'/posts/{self.post.id}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_urls_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        template_urls_names = {
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/post_detail.html': f'/posts/{self.post.pk}/'}

        for template, address in template_urls_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
