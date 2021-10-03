import wikipedia
import random
import requests
import re

DisambiguationError = wikipedia.exceptions.DisambiguationError

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

def context(word, article):
  for sentence in re.split('\n|\.', article.content):
    words = re.sub('[^\w\d\s]', '', sentence).split()
    if word in words:
      return sentence

def get_article(article_title):
  search = wikipedia.search(article_title)
  article = wikipedia.page(search[0], auto_suggest=False)
  return article

def get_random_articles():
  response = requests.get('https://en.wikipedia.org/w/api.php', params={'action': 'query', 'list':'mostviewed','pvimoffset': random.randint(0, 1000-10), 'format': 'json'})
  articles = [article['title'] for article in response.json()['query']['mostviewed']]
  return articles

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

def get_article_wordcount(article_title, word):
  article = get_article(article_title)
  words = re.sub('[^\w\d\s]', '', article.content.lower()).split()
  matches = words.count(word.lower())
  return article.title, matches