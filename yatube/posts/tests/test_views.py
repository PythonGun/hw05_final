from django.conf import settings
from django import forms
from django.test import TestCase, Client
from django.urls import reverse


from posts.models import Post, Group, User, Follow


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')
        cls.another_user_1 = User.objects.create_user(
            username='another_auth_1'
        )
        cls.another_user_2 = User.objects.create_user(
            username='another_auth_2'
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.group1 = Group.objects.create(
            title='Тестовая группа1',
            slug='test-slug1',
            description='Тестовое описание1',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст поста',
            group=cls.group
        )

        cls.post1 = Post.objects.create(
            author=cls.user,
            text='Текст поста',
            group=cls.group)

        cls.templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
            reverse('posts:index'): 'index.html',
            reverse('posts:slug', kwargs={'slug': cls.group.slug}):
            'group_list.html',
            reverse('posts:profile', kwargs={'username': cls.user.username}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': cls.post.pk}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': cls.post.pk}):
            'posts/create_post.html',
        }

        cls.field_urls_templates = [
            reverse('posts:index'),
            reverse('posts:slug', kwargs={
                'slug': cls.group.slug}),
            reverse('posts:profile', kwargs={
                'username': cls.user.username})
        ]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_authorized_client_1 = Client()
        self.another_authorized_client_1.force_login(self.another_user_1)
        self.another_authorized_client_2 = Client()
        self.another_authorized_client_2.force_login(self.another_user_2)

    def test_pages_uses_correct_template(self):
        """URL адресс использует соответствующий шаблон"""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Главная страница сформирована с правильным контекстом"""
        for post in Post.objects.all():
            response = self.authorized_client.get(reverse('posts:index'))
            page_obj = response.context['page_obj']
            self.assertIn(post, page_obj)

    def test_group_posts_page_show_correct_context(self):
        """Cтраница группы сформирована с правильным контекстом"""
        for post in Post.objects.all():
            response = self.authorized_client.get(
                reverse('posts:slug', args=[self.group.slug])
            )
            page_obj = response.context['page_obj']
            self.assertIn(post, page_obj)

    def test_post_profile_page_show_correct_context(self):
        """Страница профиля сформирована с правильным контекстом"""
        for post in Post.objects.all():
            response = self.authorized_client.get(
                reverse('posts:profile', args=[self.user.username])
            )
            page_obj = response.context['page_obj']
            self.assertIn(post, page_obj)
            self.assertEqual(
                response.context.get('author').username,
                self.user.username
            )

    def test_post_detail_page_show_correct_context(self):
        """Страница поста сформирована с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.id])
        )
        post_context = response.context['post']
        self.assertEqual(post_context, self.post)

    def test_create_post_page_show_correct_context(self):
        """Страница создания поста сформирована с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        username_context = response.context['user']
        self.assertEqual(username_context, self.user)

    def test_post_edit_page_show_correct_context(self):
        """Страница создания поста сформирована с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=[self.post.id])
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        username_context = response.context['user']
        self.assertEqual(username_context, self.user)
        is_edit_context = response.context.get('is_edit')
        self.assertTrue(is_edit_context)

    def test_page_list(self):
        """Пост с группой попал на необходимые страницы."""
        for url in self.field_urls_templates:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(len(response.context['page_obj']), 2)

    def test_profile_follow(self):
        """Авторизованный пользователь может подписываться на других
        пользователей."""
        self.another_authorized_client_1.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}
        ))
        self.assertEqual(Follow.objects.count(), 1)
        self.assertTrue(Follow.objects.filter(
            user=self.another_user_1,
            author=self.user
        ).exists())

    def test_profile_unfollow(self):
        """Авторизованный пользователь может отписываться от других
        пользователей."""
        self.another_authorized_client_1.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}
        ))
        self.another_authorized_client_1.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user.username}
        ))
        self.assertEqual(Follow.objects.count(), 0)

    def test_profile_follow_page(self):
        """Новая запись пользователя появляется в ленте подписчиков."""
        self.another_authorized_client_1.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username}
        ))
        response_1 = self.another_authorized_client_1.get(reverse(
            'posts:follow_index'
        ))
        self.assertIn(
            self.post,
            response_1.context.get('page_obj').object_list
        )
        response_2 = self.another_authorized_client_2.get(reverse(
            'posts:follow_index'
        ))
        self.assertNotIn(
            self.post,
            response_2.context.get('page_obj').object_list
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = [
            Post.objects.create(
                text='Пост №' + str(i),
                author=cls.user,
                group=cls.group
            )
            for i in range(13)]

    def setUp(self):
        self.client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_index_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        page_obj = response.context['page_obj']
        number_obj = page_obj.paginator.get_page('1').object_list.count()
        self.assertEqual(number_obj, settings.PAGE_NUM)

    def test_second_page_contains_three_records(self):
        response = self.client.get(
            reverse('posts:index') + '?page=2'
        )
        page_obj = response.context['page_obj']
        number_obj = page_obj.paginator.get_page('2').object_list.count()
        self.assertEqual(number_obj, 3)
