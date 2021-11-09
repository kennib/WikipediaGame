import pytest

import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import game
import rounds
import wiki


def init_round(round=1, players=1):
  room = game.Room('test room')

  for n in range(players):
    room.add_player(f'player {n+1}')

  room.next_round()

  while room.round_number != round:
    room.next_round()

  return room

#
# JSON encode/decode tests
#

def test_json_encode():
  room = init_round()
  json_string = json.dumps(room)

  assert type(json_string) == str

  data = json.loads(json_string)

  assert set(data['players']) == set(room.players)
  assert set(data['state']) == set(room.state)

#
# Answer submission tests
#

def test_answer_submission():
  room = init_round()

  assert room.state == 'round'

  room.receive_answer('player 1', 'dog')

  if room.round_complete():
    room.score_round()

  assert room.state == 'round scores'

def test_ambiguous_answer_submission():
  room = init_round()

  assert room.state == 'round'

  try:
    room.receive_answer('player 1', 'butt')
    assert False
  except wiki.DisambiguationError as e:
    assert type(e) == wiki.DisambiguationError

  if room.round_complete():
    room.score_round()

  assert room.state == 'round'

def test_invalid_answer_submission():
  room = init_round(2)
  room.setup_round('Vampire Weekend')

  assert room.state == 'round'
  assert type(room.round) == rounds.MostCommonLinksRound

  try:
    room.receive_answer('player 1', 'Vampire')
    assert False
  except rounds.InvalidAnswerError as e:
    assert type(e) == rounds.InvalidAnswerError

  if room.round_complete():
    room.score_round()

  assert room.state == 'round'

def test_invalid_article_answer_submission():
  room = init_round(2)
  room.setup_round('The Justice League')

  assert room.state == 'round'
  assert type(room.round) == rounds.MostCommonLinksRound

  try:
    room.receive_answer('player 1', 'Bamtan')
    assert False
  except wiki.NoArticleError as e:
    assert type(e) == wiki.NoArticleError

  if room.round_complete():
    room.score_round()

  assert room.state == 'round'