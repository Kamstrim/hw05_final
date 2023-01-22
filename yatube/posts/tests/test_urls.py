from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(
            username='Vova',
            email='ychag@example.com',
            password='test'
        )
        cls.another_test_user = User.objects.create(
            username='Boris',
            email='ychag@example.com',
            password='test'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            pub_date=timezone.now(),
            author=cls.test_user,
            group=Group.objects.create(
                title='Тестовая группа',
                slug='test-group',
                description='Тестовое описание'
            )
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user)
        self.authorized_another_client = Client()
        self.authorized_another_client.force_login(self.another_test_user)

    def test_pages_for_all(self):
        """Доступность страниц для неавторизированного пользователя."""

        self.pages_for_all = (
            '/',
            f'/group/{self.post.group.slug}/',
            f'/profile/{self.test_user.username}/',
            f'/posts/{self.post.id}/'
        )

        for page in self.pages_for_all:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_for_authorized(self):
        """Доступность страниц для авторизированного пользователя."""

        self.pages_for_authorized = (
            f'/posts/{self.post.id}/edit/',
            '/create/',
        )
        for page in self.pages_for_authorized:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_redirect(self):
        """Тест корректного редиректа."""

        self.pages_for_authorized = (
            f'/posts/{self.post.id}/edit/',
            '/create/',
            f'/posts/{self.post.id}/comment/',
        )
        for page in self.pages_for_authorized:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_page_edit_for_not_author(self):
        """Страница редактирования доступна только автору."""
        response = self.authorized_another_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertRedirects(
            response,
            f'/posts/{self.post.id}/'
        )

    def test_home_urls_uses_correct_template(self):
        """Корректность шаблонов."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.post.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.test_user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',

        }
        for url_name, template_name in templates_url_names.items():
            with self.subTest(url_name=url_name):
                response = self.authorized_client.get(url_name)
                self.assertTemplateUsed(response, template_name)

    def test_not_correct_url(self):
        response = self.guest_client.get('/unexciting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
