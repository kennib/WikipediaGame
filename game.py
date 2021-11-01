import wiki
import random
import string
from time import time

from rounds import ROUNDS

POINTS_PER_ROUND = 1000

def generate_room_code(exclude=[]):
  room_code = None

  while not room_code or room_code in exclude:
    letters = random.choices(string.ascii_uppercase, k=4)
    room_code = ''.join(letters)

  return room_code

class Room():
  def __init__(self, room_code, round_time=60):
    self.code = room_code
    self.players = set()
    self.state = 'waiting room'

    self.finish_time = None
    self.round_time = round_time
    self.round = None

    self.final_results = {}

  def add_player(self, player):
    self.players.add(player)
    self.final_results[player] = {'player': player, 'score': 0}

  def next_round(self):
    if self.state == 'waiting room':
      self.round_number = 0

    self.results = {}
    if self.round_number < len(ROUNDS):
      self.round_number += 1
      self.round = ROUNDS[self.round_number - 1]()
      if hasattr(self.round, 'setup'):
        self.state = 'round setup'
        self.player_choice = {'player': random.choice(list(self.players)), 'options':  wiki.get_random_articles()}
      else:
        self.state = 'round'
        self.finish_time = int(time()) + self.round_time
    else:
      self.state = 'final scores'
      
  def receive_answer(self, player, answer):
    self.results[player] = {
      'player': player,
      'answer': answer,
    }

    if answer:
      self.round.validate_answer(answer) # Will raise an exception if the answer is invalid

      score = self.round.score(answer)
      
      self.results[player] = {
        'player': player,
        'answer': answer,
        'article': {
          'title': score.article.title,
          'url': score.article.url,
        },
        'raw_score': score.raw_score,
        'score': score.display_score or score.raw_score,
        'details': score.details,
      }
    else:
      self.results[player] = {
        'player': player,
        'raw_score': 0,
        'score': '-',
      }

  def round_complete(self):
    submissions = [result for result in self.results.values() if result.get('raw_score') != None]
    return len(submissions) == len(self.players)

  def waiting_for_players(self):
   players = [player for player in self.players if not player in self.results]
   return players

  def score_round(self):
    self.state = 'round scores'

    for player in self.players:
      if player not in self.results:
        self.receive_answer(player, None)

    total_score = 0 
    for result in self.results.values():
      if result.get('raw_score'):
        total_score += result['raw_score']

    for player in self.players:
      if total_score == 0:
        self.results[player]['normalised_score'] = 0
      elif self.results[player].get('raw_score'):
        self.results[player]['normalised_score'] = round((self.results[player]['raw_score'] / total_score) * POINTS_PER_ROUND)
      else:
        self.results[player]['normalised_score'] = 0
      self.final_results[player]['score'] += self.results[player]['normalised_score']
      self.results[player]['running_score'] = self.final_results[player]['score']

  def round_results(self):
    results = [self.results.get(player, {}) for player in self.players]
    return sorted(results, key=lambda result: result.get('normalised_score', 0), reverse=True)

  def current_state(self, player=None):
    current_state = {
      'serverTime': int(time()),
      'state': self.state,
      'players': list(self.players)
    }

    if self.state == 'round setup':
      current_state['round'] = {
        'playerChoice': self.player_choice,
        'title': self.round.title,
        'number': self.round_number,
      }
    elif self.state == 'round':
      current_state['round'] = {
        'title': self.round.title,
        'number': self.round_number,
        'time': self.round_time,
        'finishTime': self.finish_time,
        'question': {
            'description': self.round.question,
            'data': self.round.data
        },
        'submitted': self.results.get(player, {}).get('raw_score') != None,
        'answer': None,
        'disambiguation': None,
        'invalidAnswer': None,
        'waitingFor': self.waiting_for_players(),
      }
    elif self.state == 'round scores':
      current_state['round'] = {
        'title': self.round.title,
        'number': self.round_number,
        'question': {
          'description': self.round.question,
          'data': self.round.data
        },
        'results': self.round_results()
      }
    elif self.state == 'final scores':
      current_state['results'] = sorted(self.final_results.values(), key=lambda result: result.get('score', 0), reverse=True)

    return current_state

  def setup_round(self, article_title):
    self.round.setup(article_title)
    self.finish_time = int(time()) + self.round_time
    self.state = 'round'