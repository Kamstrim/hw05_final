from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django import forms

import shutil
import tempfile

from ..models import Post, Group, Follow

User = get_user_model()
TEST_OF_POST: int = 13
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(title='Тестовая группа',
                                         slug='test_group')

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        bilk_post: list = []
        for i in range(TEST_OF_POST):
            bilk_post.append(Post(text=f'Тестовый текст {i}',
                                  group=self.group,
                                  author=self.user))
        Post.objects.bulk_create(bilk_post)

    def test_correct_page_context(self):
        templates_for_test = (
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}
                    ),
            reverse('posts:profile',
                    kwargs={'username': f''
                                        f'{self.user.username}'}),
        )
        for template in templates_for_test:
            with self.subTest(template=template):
                cache.clear()
                response_for_first_page = self.authorized_client.get(template)
                self.assertEqual(len(
                    response_for_first_page.context['page_obj']
                ), 10)
                response_for_two_page = self.authorized_client.get(
                    f'{template}?page=2'
                )
                self.assertEqual(len(
                    response_for_two_page.context['page_obj']
                ), 3)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание'
        )
        cls.user = User.objects.create_user(
            username='test',
            email='kenaa@example.com',
            password='test_password'
        )

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
            image=cls.image,
        )
        cls.following_user = User.objects.create(username='following')
        cls.post_following_user = Post.objects.create(
            text='Тестовый текст',
            author=cls.following_user,
            image=cls.post.image,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.user = User.objects.get(username='test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user.username}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}
                    ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}
                    ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                cache.clear()
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][1]
        task_text_0 = first_object.text
        task_group_0 = first_object.group.title
        self.assertEqual(task_text_0, 'Тестовый текст')
        self.assertEqual(task_group_0, 'Тестовая группа')

    def test_group_list_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                                kwargs={'slug': self.post.group.slug})))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_group_0 = first_object.group.title
        task_slug_0 = first_object.group.slug
        self.assertEqual(task_text_0, 'Тестовый текст')
        self.assertEqual(task_group_0, 'Тестовая группа')
        self.assertEqual(task_slug_0, 'test-group')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:profile',
                                kwargs={'username': self.user.username})))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_username_0 = first_object.author.username
        self.assertEqual(task_text_0, 'Тестовый текст')
        self.assertEqual(task_username_0, 'test')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                                kwargs={'post_id': self.post.id})))
        post_detail = response.context['post']
        self.assertEqual(post_detail.text, 'Тестовый текст')
        self.assertEqual(post_detail.id, 1)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_edit',
                                kwargs={'post_id': self.post.id})))
        field_text = response.context.get('form').instance.text
        self.assertEqual(field_text, 'Тестовый текст')

    def test_new_post_in_group(self):
        """Дополнительная проверка при создании поста."""
        another_test_group = Group.objects.create(
            title='Тестовая группа2',
            slug='test-group2',
            description='Тестовое описание группы2'
        )
        posts_count_all = Post.objects.all().count()
        posts_count_group = Post.objects.filter(group=self.group).count()
        posts_count_user = Post.objects.filter(author=self.user).count()
        Post.objects.create(
            text='Тестовый пост от другого автора',
            author=self.user,
            group=another_test_group)
        posts_count_all_new = Post.objects.all().count()
        posts_count_group_new = Post.objects.filter(group=self.group).count()
        posts_count_user_new = Post.objects.filter(author=self.user).count()
        self.assertNotEqual(posts_count_all_new, posts_count_all)
        self.assertNotEqual(posts_count_user_new, posts_count_user)
        self.assertEqual(posts_count_group_new, posts_count_group)

    def test_image_content(self):
        """Наличие картинки в посте через словарь context"""
        templates_pages_names = {
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ),
            reverse('posts:profile',
                    kwargs={'username': self.user.username}
                    )
        }
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                cache.clear()
                response = self.authorized_client.get(reverse_name)
                first_object = response.context['page_obj'][0]
                post_image_0 = first_object.image
                self.assertEqual(post_image_0.name, 'posts/small.gif')

        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id})
        )
        first_object = response.context['post']
        post_image_0 = first_object.image
        self.assertEqual(post_image_0.name, 'posts/small.gif')

    def test_cache_index(self):
        """Проверка кэша индекса постов."""
        response_cache_clear_posts_ok = self.authorized_client.get(
            reverse('posts:index')
        )
        Post.objects.get(id=1).delete()
        response_cache_ok_posts_delete = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(
            response_cache_clear_posts_ok.content,
            response_cache_ok_posts_delete.content)
        cache.clear()
        response_cache_clear_posts_delete = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertNotEqual(
            response_cache_clear_posts_ok.content,
            response_cache_clear_posts_delete
        )

    def test_follow_authorized_client(self):
        """Проверка возможности подписки авторизованного клиента."""
        response_before_follow = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response_before_follow.context['page_obj']), 0)

        Follow.objects.create(
            user=self.user,
            author=self.following_user
        )

        response_after_follow = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response_after_follow.context['page_obj']), 1)
        self.assertIn(
            self.post_following_user,
            response_after_follow.context['page_obj']
        )

        Follow.objects.filter(
            user=self.user,
            author=self.following_user
        ).delete()

        response_after_delete_follow = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(
            response_after_delete_follow.context['page_obj']
        ), 0)
        self.assertNotIn(
            self.post_following_user,
            response_after_delete_follow.context['page_obj']
        )
