from http import HTTPStatus
from django.test import TestCase, Client

from posts.models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.author = User.objects.create_user(username='test_author')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)

        cls.group = Group.objects.create(
            title='test_group_title',
            slug='test_group_slug',
            description='test_group_descrioption'
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.author
        )

        cls.templates_url_names = {
            '/': 'index.html',
            f'/group/{cls.group.slug}/': 'group_list.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html',
        }

        cls.urls = {
            '/': HTTPStatus.OK.value,
            f'/group/{cls.group.slug}/': HTTPStatus.OK.value,
            f'/profile/{cls.user.username}/': HTTPStatus.OK.value,
            f'/posts/{cls.post.id}/': HTTPStatus.OK.value,
            '/create/': HTTPStatus.FOUND,
            f'/posts/{cls.post.id}/edit/': HTTPStatus.FOUND,
        }

        cls.urls_page = {
            '/',
            f'/group/{cls.group.slug}/',
            f'/profile/{cls.user.username}/',
            f'/posts/{cls.post.id}/',
            '/create/',
            f'/posts/{cls.post.id}/edit/',
        }

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for adress, template in PostURLTests.templates_url_names.items():
            with self.subTest(adress=adress):
                response = PostURLTests.authorized_author.get(
                    adress, follow=True
                )
                self.assertTemplateUsed(response, template)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls(self):
        """Проверка работы страниц"""
        for adress in self.urls_page:
            with self.subTest(adress=adress):
                response = PostURLTests.authorized_author.get(
                    adress, follow=True
                )
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_guest(self):
        """Проверка работы страниц для  неавторизованного пользователя"""
        for adress, expected in self.urls.items():
            with self.subTest(adress=adress):
                response = PostURLTests.guest_client.get(
                    adress
                )
                self.assertEqual(response.status_code, expected)

    def unexisting_page_does_not_exist(self):
        """Несуществующая страница выдает ошибку 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
