from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Задача организации, в особенности же постоянный '
                 'количественный рост и сфера нашей активности '
                 'создаёт предпосылки качественно новых шагов '
                 'для направлений прогрессивного развития! '
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        self.assertEqual(str(post), post.text[:15])
        self.assertEqual(str(group), group.title)

    def test_text_label(self):
        post = PostModelTest.post
        self.assertEqual(
            post._meta.get_field('text').verbose_name, 'Текст поста'
        )

    def test_text_help_text(self):
        post = PostModelTest.post
        self.assertEqual(
            post._meta.get_field('text').help_text, 'Введите текст поста'
        )

    def test_pub_date_label(self):
        post = PostModelTest.post
        self.assertEqual(
            post._meta.get_field('pub_date').verbose_name, 'Дата публикации'
        )

    def test_author_label(self):
        post = PostModelTest.post
        self.assertEqual(
            post._meta.get_field('author').verbose_name, 'Автор'
        )

    def test_group_label(self):
        post = PostModelTest.post
        self.assertEqual(
            post._meta.get_field('group').verbose_name, 'Группа'
        )

    def test_group_help_text(self):
        post = PostModelTest.post
        self.assertEqual(
            post._meta.get_field('group').help_text,
            'Группа, к которой будет относиться пост'
        )
