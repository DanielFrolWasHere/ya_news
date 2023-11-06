import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
        date=timezone.now(),
    )
    return news


@pytest.fixture
def news_count_on_homepage():
    return settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def news_bulk(news, news_count_on_homepage):
    today = datetime.today()
    news_bulk = []
    for index in range(news_count_on_homepage + 1):
        news = News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        news_bulk.append(news)
    News.objects.bulk_create(news_bulk)
    return news_bulk


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
        created=timezone.now(),
    )
    return comment


@pytest.fixture
def comments_bulk(comment):
    for index in range(2):
        comment = Comment.objects.create(
            news=comment.news,
            author=comment.author,
            text=f'Tекст {index}',
        )
        comment.created = timezone.now() + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data():
    form_data = {'text': 'Новый текст'}
    return form_data


@pytest.fixture
def news_pk_arg(news):
    return news.pk,


@pytest.fixture
def comment_pk_arg(comment):
    return comment.pk,

