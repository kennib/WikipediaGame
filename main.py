import requests
import wikipedia
import re
import random

def choose_option(name, options):
  for i, option in enumerate(options):
    print(f'{i}) {option}')
  choice = int(input(f'Choose a {name}: '))
  return options[choice]

def choose_random_article():
  response = requests.get('https://en.wikipedia.org/w/api.php', params={'action': 'query', 'list':'mostviewed','pvimoffset': random.randint(0, 1000-10), 'format': 'json'})
  articles = [article['title'] for article in response.json()['query']['mostviewed']]
  print(articles)
  article = get_article(choose_option('article', articles))
  print(article.title)
  print(article.summary[:250])
  return article

def get_random_month():
  year = random.randint(2016, 2021)
  month = random.randint(1,12)
  print(year, month)
  return year, month

def get_random_word():
  words = open('nounlist.txt').readlines()
  word = random.choice(words).strip()
  print(word)
  return word

def get_article(article_title):
  search = wikipedia.search(article_title)
  try:
    article = wikipedia.page(search[0], auto_suggest=False)
  except wikipedia.exceptions.DisambiguationError as e:
    choice = choose_option('article', e.options)
    article = wikipedia.page(choice, auto_suggest=False)
  return article

def get_pageviews(article, date):
  year, month = date
  if month == 12:
    end_year, end_month = year+1, 1
  else:
    end_year, end_month = year, month+1
  response = requests.get(f'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{article}/monthly/{year}{month:02d}0100/{end_year}{end_month:02d}0100', headers={
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
  })
  try:
    views = response.json()['items'][0]['views']
  except KeyError:
    views = 0
  return views
  

def guess_article_with_most_words(word):
  article_title = get_answer(f'Find the page with the most {word}: ', [word])
  article = get_article(article_title)

  words =  re.sub('[^\w\d\s]', '', article.content.lower()).split()
  matches = words.count(word.lower())

  print(f'The {article.title} article has {matches} {word}s')

  if matches:
    print(context(word, article.content))

  return matches

def guess_article_with_most_common_links(article):
  article_title = get_answer(f'Find the page with the common links with {article.title}: ', article.title.split())
  guessed_article = get_article(article_title)

  common_links = set(article.links) & set(guessed_article.links)

  print(f'The {guessed_article.title} article has {len(common_links)} links in common with {article.title}')
  print(common_links)

  return len(common_links)

def guess_article_with_most_views(date):
  year, month = date
  article_title = get_answer(f'Find the most popular article for {month}/{year}: ')
  article = get_article(article_title)
  
  pageviews = get_pageviews(article.title.replace(' ', '_'), date)

  print(f'The {article.title} article has {pageviews:,} pageviews')

  return pageviews

def get_answer(prompt, invalid_inputs=None):
  invalid_inputs = invalid_inputs or []
  answer = None

  while not answer:
    answer = input(prompt)
    if set(answer.split()) & set(invalid_inputs):
      print(f'You can\'t use {answer}')
      answer = None
  
  return answer

def context(word, article):
  for sentence in re.split('\n|\.', article):
    words = re.sub('[^\w\d\s]', '', sentence).split()
    if word in words:
      return sentence

def round(setup, ask):
  if setup:
    context = setup()
  else:
    context = None
  
  player1 = ask(context)
  player2 = ask(context)

  while player1 == 0 and player2 == 0:
    retry = input('Retry? Y/N: ').lower()
    if retry.lower() == 'y':
      player1 = ask(context)
      player2 = ask(context)
    else:
      break

  if player1 > player2:
    print('Player 1 wins!')
  elif player1 < player2:
    print('Player 2 wins!')
  else:
    print('It\'s a draw!')

if __name__ == '__main__':
  print('Round 1')
  round(get_random_word, guess_article_with_most_words)
  print()
  print('Round 2')
  round(choose_random_article, guess_article_with_most_common_links)
  print()
  print('Round 3')
  round(get_random_month, guess_article_with_most_views)