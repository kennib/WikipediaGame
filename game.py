import wiki
import random

class Round():
  def __init__(self):
    self.question = ''

  def score(self, answer):
    raise Exception('Not implemented')

class MostWordsRound(Round):
  def __init__(self):
    self.word = wiki.get_random_word()
    self.question = f'Which page has the most {self.word}?'

  def score(self, answer):
    return wiki.get_article_wordcount(answer, self.word)

class MostCommonLinksRound(Round):
  def __init__(self):
    self.article_title = ''
    self.question = ''

  def setup(self, article_title):
    self.article_title = article_title
    self.question = f'Find the page with the common links with {self.article_title}'

  def score(self, answer):
    return wiki.get_common_links(self.article_title, answer)

class MostViewsRound(Round):
  def __init__(self):
    self.year, self.month = wiki.get_random_month()
    self.question = f'Find the most popular article for {self.month}/{self.year}'

  def score(self, answer):
    article = wiki.get_article(answer)
    views = wiki.get_pageviews(article.title.replace(' ', '_'), (self.year, self.month))
    return article.title, views

ROUNDS = [MostWordsRound, MostCommonLinksRound, MostViewsRound]

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
      self.results[player]['score'] = score
    else:
      self.results[player]['article'] = None
      self.results[player]['score'] = 0
  
  def round_complete(self):
    submissions = [result for result in self.results.values() if result.get('score') != None]
    return len(submissions) == len(self.players)

  def waiting_for_players(self):
   players = [player for player in self.players if not player in self.results]
   return players

  def score_round(self):
    self.state = 'round scores'

    for player in self.players:
      if player not in self.results:
        self.receive_answer(player, None)
      
      self.final_results[player]['score'] += self.results[player]['score']

  def round_results(self):
    results = [self.results[player] for player in self.players]
    return sorted(results, key=lambda result: result.get('score', 0), reverse=True)

  def current_state(self, player=None):
    current_state = { 'state': self.state }

    if self.state == 'round setup':
      current_state['playerChoice'] = self.player_choice
    elif self.state == 'round':
      current_state['roundTime'] = self.round_time
      current_state['round'] = self.round_number
      current_state['question'] = self.round.question
      current_state['submitted'] = self.results.get(player, {}).get('score') != None
      current_state['answer'] = None
      current_state['disambiguation'] = None
      current_state['waitingFor'] = self.waiting_for_players()
    elif self.state == 'round scores':
      current_state['round'] = self.round_number
      current_state['question'] = self.round.question
      current_state['results'] = self.round_results()
    elif self.state == 'final scores':
      current_state['results'] = sorted(self.final_results.values(), key=lambda result: result.get('score', 0), reverse=True)

    return current_state

  def setup_round(self, article_title):
    print('setup_round')
    self.round.setup(article_title)
    self.state = 'round'