import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from ..models import Post, User, Group, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='test_user',
            email='kenaa@example.com',
            password='test_password'
        )
        cls.test_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='test.gif',
            content=cls.test_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'image': self.uploaded,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_post = Post.objects.latest('text', 'group', 'image')
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group.id, form_data['group'])
        self.assertEqual(last_post.image, 'posts/test.gif')

    def test_edit_post(self):
        """Валидная форма изменяет пост"""
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user
        )
        post_first = self.post
        form_data = {
            'text': 'Измененный текст'
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_first.id}),
            data=form_data,
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        post_result = Post.objects.get(id=post_first.id)
        self.assertEqual(post_result.text,
                         form_data['text'], 'Текст не изменился')

    def test_coment_post(self):
        """Валидная форма добавляет комментарий к посту"""
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
        )
        comment_count = post.comments.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(post.comments.count(), comment_count + 1)
        comment_for_post = Comment.objects.get(id=post.id)
        self.assertEqual(comment_for_post.text,
                         form_data['text'])
