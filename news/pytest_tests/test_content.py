import pytest

from django.urls import reverse

from news.forms import CommentForm
from news.models import News


pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('news_bulk')
def test_news_count(client, news_count_on_homepage):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == news_count_on_homepage


@pytest.mark.usefixtures('news_bulk')
def test_news_order(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures('comments_bulk')
def test_comments_order(client, news_pk_arg):
    url = reverse('news:detail', args=(news_pk_arg))
    response = client.get(url)
    object_list = response.context['news']
    all_comments = object_list.comment_set.all()
    assert all_comments[0].created <= all_comments[1].created


@pytest.mark.parametrize(
    'parametrized_client, form',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
def test_form_availability_for_different_users(parametrized_client, news_pk_arg, form):
    url = reverse('news:detail', args=(news_pk_arg))
    response = parametrized_client.get(url)
    assert ('form' in response.context) == form
    if form:
        assert isinstance(response.context['form'], CommentForm)
