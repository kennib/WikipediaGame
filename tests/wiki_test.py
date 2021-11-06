import pytest
from unittest.mock import MagicMock, patch

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import wiki

CONTENT = 'This a sentence about cats. This a sentence about dogs.\nThis paragraph is about giraffes. Giraffes are pretty tall.'


def test_context():
    mock_article = MagicMock()
    mock_article.content = CONTENT
    example = wiki.context('cats', mock_article)
    assert example is not None
    assert 'cats' in example


def test_context_different_cases():
    mock_article = MagicMock()
    mock_article.content = CONTENT
    example = wiki.context('Cats', mock_article)
    assert example is not None
    assert 'cats' in example

def test_random_image():
  article_title = 'Begbie'
  article = wiki.get_article(article_title)
  with patch('wiki.get_article') as get_article:
    get_article.return_value = article

    title, url, image_article = wiki.get_random_image()
    assert title == 'File:Vintage road sign.East Lothian.jpg'
    assert url == 'https://upload.wikimedia.org/wikipedia/commons/9/9a/Vintage_road_sign.East_Lothian.jpg'
    assert image_article.title == article.title

def test_random_image_missing():
  article_title = '7784 Watterson'
  article = wiki.get_article(article_title)
  with patch('wiki.get_article') as get_article:
    get_article.return_value = article

    try:
      title, url, image_article = wiki.get_random_image()
      print(title, url, image_article)
      assert False
    except wiki.NoImageError as e:
      assert type(e) == wiki.NoImageError