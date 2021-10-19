import wiki
import random

from rounds import ROUNDS

POINTS_PER_ROUND = 1000

class Room():
  def __init__(self, room_code, round_time=30):
    self.code = room_code
    self.players = set()
    self.state = 'waiting room'

    self.round_time = round_time
    self.round = None

    self.final_results = {}

  def add_player(self, player):
    self.players.add(player)
    self.final_results[player] = {'player': player, 'score': 0}

  def next_round(self):
    if self.state == 'waiting room':
      self.round_number = 0

    print('CURRENT ROUND', self.round_number, self.state)

    self.results = {}
    if self.round_number < len(ROUNDS):
      self.round_number += 1
      self.round = ROUNDS[self.round_number - 1]()
      self.state = 'round'
      if hasattr(self.round, 'setup'):
        self.state = 'round setup'
        self.player_choice = {'player': random.choice(list(self.players)), 'options':  wiki.get_random_articles()}
    else:
      self.state = 'final scores'

    print('CURRENT ROUND', self.round_number, self.state)
      
  def receive_answer(self, player, answer):
    self.results[player] = {
      'player': player,
      'answer': answer,
    }

    if answer:
      article_title, score = self.round.score(answer)
      print(f'{article_title} {score}')
      
      self.results[player]['article'] = article_title
      self.results[player]['raw_score'] = score
    else:
      self.results[player]['article'] = None
      self.results[player]['raw_score'] = 0
  
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

    total_score = sum([self.results[player]['raw_score'] for player in self.results.keys()])

    for player in self.players:
      if total_score == 0:
        self.results[player]['normalised_score'] = 0
      else:
        self.results[player]['normalised_score'] = round((self.results[player]['raw_score'] / total_score) * POINTS_PER_ROUND)
      self.final_results[player]['score'] += self.results[player]['normalised_score']

  def round_results(self):
    results = [self.results[player] for player in self.players]
    return sorted(results, key=lambda result: result.get('normalised_score', 0), reverse=True)

  def current_state(self, player=None):
    current_state = { 'state': self.state, 'players': list(self.players) }

    if self.state == 'round setup':
      current_state['playerChoice'] = self.player_choice
    elif self.state == 'round':
      current_state['roundTime'] = self.round_time
      current_state['round'] = self.round_number
      current_state['question'] = {
        'description': self.round.question,
        'data': self.round.data
      }
      current_state['submitted'] = self.results.get(player, {}).get('raw_score') != None
      current_state['answer'] = None
      current_state['disambiguation'] = None
      current_state['waitingFor'] = self.waiting_for_players()
    elif self.state == 'round scores':
      current_state['round'] = self.round_number
      current_state['question'] = {
        'description': self.round.question,
        'data': self.round.data
      }
      current_state['results'] = self.round_results()
    elif self.state == 'final scores':
      current_state['results'] = sorted(self.final_results.values(), key=lambda result: result.get('score', 0), reverse=True)

    return current_state

  def setup_round(self, article_title):
    print('setup_round')
    self.round.setup(article_title)
    self.state = 'round'