import pytest

import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import rounds

#
# JSON encode/decode tests
#

def test_json_encode():
  round = rounds.HighestWordCountRound()
  json_string = json.dumps(round)

  assert type(json_string) == str

  data = json.loads(json_string)

  assert 'word' in data
  assert 'question' in data
  assert 'title' in data