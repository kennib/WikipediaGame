import pytest
from unittest.mock import MagicMock

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