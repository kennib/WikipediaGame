import wikipedia
import random
import requests
import re

DisambiguationError = wikipedia.exceptions.DisambiguationError

def get_random_month():
  year = random.randint(2016, 2021)
  month = random.randint(1,12)
  return year, month

def get_random_word():
  words = open('nounlist.txt').readlines()
  word = random.choice(words).strip()
  return word

def context(word, article):
  for sentence in re.split('\n|\.', article.content):
    words = re.sub('[^\w\d\s]', '', sentence).split()
    if word in words:
      return sentence + '.'

def get_article(article_title):
  search = wikipedia.search(article_title)
  article = wikipedia.page(search[0], auto_suggest=False)
  return article

def get_random_articles():
  response = requests.get('https://en.wikipedia.org/w/api.php', params={'action': 'query', 'list':'mostviewed','pvimoffset': random.randint(0, 1000-10), 'format': 'json'})
  articles = [article['title'] for article in response.json()['query']['mostviewed']]
  return articles

def get_random_image():
  response = requests.get('https://en.wikipedia.org/w/api.php', params={'action': 'query', 'list':'mostviewed', 'pvimoffset': random.randint(0, 1000), 'pvlimit': 1, 'format': 'json'})

  article_title = response.json()['query']['mostviewed'][0]['title']
  article = get_article(article_title)

  image = None
  while image == None:
    response = requests.get(f'https://en.wikipedia.org/w/api.php', {'action': 'query', 'generator': 'images', 'prop': 'imageinfo', 'titles': article_title, 'iiprop': 'url|dimensions', 'format': 'json'})

    images = response.json().get('query', {}).get('pages', {}).values()
    content_images = [image for image in images if image['imagerepository'] != 'local']

    if content_images:
      image = random.choice(content_images)
    else:
      image = None

  return image['title'], image['imageinfo'][0]['url'], article

def get_pages_containing_image(image_title):
  response = requests.get(f'https://en.wikipedia.org/w/api.php', {'action': 'query', 'list':'imageusage', 'iutitle': image_title, 'iulimit': 500, 'format': 'json'})

  try:
    image_usages = response.json().get('query').get('imageusage')
    linked_pages = [page.get('title') for page in image_usages]
  except (KeyError, IndexError):
    linked_pages = []

  return linked_pages

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

def get_article_wordcount(article, word):
  words = re.sub('[^\w\d\s]', '', article.content.lower()).split()
  matches = words.count(word.lower())
  return matches

def get_common_links(article_title, guessed_article_title):
  article = get_article(article_title)
  guessed_article = get_article(guessed_article_title)
  common_links = set(article.links) & set(guessed_article.links)
  return guessed_article.title, len(common_links)
