import pytest

from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertRedirects, assertFormError
from pytils.translit import slugify

from news.forms import BAD_WORDS, WARNING, CommentForm

from news.models import News, Comment

pytestmark = pytest.mark.django_db




def test_anonymous_user_cant_create_comment(client, news_pk_arg, form_data):
    url = reverse('news:detail', args=(news_pk_arg))
    response = client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_user_can_create_comment(author_client, news_pk_arg, form_data):
    url = reverse('news:detail', args=(news_pk_arg))
    response = author_client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_user_cant_use_bad_words(author_client, news_pk_arg):
    url = reverse('news:detail', args=(news_pk_arg))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, comment_pk_arg, news_pk_arg):
    news_url = reverse('news:detail', args=(news_pk_arg))
    url_to_comments = news_url + '#comments'
    delete_url = reverse('news:delete', args=(comment_pk_arg))
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(reader_client, comment_pk_arg):
    delete_url = reverse('news:delete', args=(comment_pk_arg))
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, comment, comment_pk_arg, form_data, news_pk_arg):
    news_url = reverse('news:detail', args=(news_pk_arg))
    url_to_comments = news_url + '#comments'
    edit_url = reverse('news:edit', args=(comment_pk_arg))
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(reader_client, comment, form_data, comment_pk_arg):
    COMMENT_TEXT = Comment.objects.get(id=comment.id)
    edit_url = reverse('news:edit', args=(comment_pk_arg))
    response = reader_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT.text
