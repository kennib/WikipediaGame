import wikipedia # type: ignore
import random
import requests
import re
from flask import current_app as app

# Articles if the most popular articles API is not working
PLACEHOLDER_ARTICLES =  ['Bernie Sanders', 'Pie', 'Donkey', 'Calculus', 'The Shining (Film)', 'The Beatles', 'Mahogony']

DisambiguationError = wikipedia.exceptions.DisambiguationError
class NoArticleError(Exception):
  pass
class NoImageError(Exception):
  pass

class Article(dict):
  def __init__(self, article):
    self.__dict__ = self
    self.title = article.title
    self.url = article.url
    self.content = article.content
    self.links = article.links
    self.summary = article.summary

def get_random_month():
  year = random.randint(2016, 2021)
  month = random.randint(1,12)
  return year, month

def get_random_word():
  words = open('data/nounlist.txt').readlines()
  word = random.choice(words).strip()
  return word

def context(word, article):
  for sentence in re.split('\n|\.', article.content):
    words = map(str.lower, re.sub('[^\w\d\s]', '', sentence).split())
    if word.lower() in words:
      return sentence + '.'

def summarise(article):
  sentences = re.split('\n|\.', article.summary)
  return sentences[0] if sentences else ''

def get_article(article_title):
  app.logger.info(f'Searching for {article_title}')
  search = wikipedia.search(article_title)
  if search:
    app.logger.info(f'Getting first returned article')
    article = wikipedia.page(search[0], auto_suggest=False)
    return Article(article)
  else:
    raise NoArticleError(f'Could not find an article for {article_title}')

def get_random_articles():
  response = requests.get('https://en.wikipedia.org/w/api.php', params={'action': 'query', 'list':'mostviewed','pvimoffset': random.randint(0, 1000-10), 'format': 'json'})
  articles = [article['title'] for article in response.json()['query']['mostviewed']]

  if articles:
    return articles
  else:
    return PLACEHOLDER_ARTICLES

def get_random_image():
  response = requests.get('https://en.wikipedia.org/w/api.php', params={'action': 'query', 'list':'mostviewed', 'pvimoffset': random.randint(0, 1000), 'pvlimit': 1, 'format': 'json'})

  app.logger.info('Choosing most viewed article with image')
  most_viewed = response.json()['query']['mostviewed']
  if most_viewed:
    article_title = most_viewed[0]['title']
  else:
    article_title = random.choice(PLACEHOLDER_ARTICLES)
  app.logger.info('Getting article with image')
  article = get_article(article_title)
  app.logger.info('Got article with image')

  response = requests.get(f'https://en.wikipedia.org/w/api.php', {'action': 'query', 'generator': 'images', 'prop': 'imageinfo', 'titles': article.title, 'iiprop': 'url|dimensions', 'format': 'json'})

  images = response.json().get('query', {}).get('pages', {}).values()
  content_images = [image for image in images if image['imagerepository'] != 'local' and image['imageinfo'][0]['height'] > 100]

  if content_images:
    image = random.choice(content_images)
    image_title = image['title']
    image_url = image['imageinfo'][0]['url']
  else:
    raise NoImageError(f'Cannot find any images on the {article_title} page')

  return image_title, image_url, article

def get_pages_containing_image(image_title):
  response = requests.get(f'https://en.wikipedia.org/w/api.php', {'action': 'query', 'list':'imageusage', 'iutitle': image_title, 'iulimit': 500, 'format': 'json'})

  try:
    image_usages = response.json().get('query').get('imageusage')
    linked_pages = [page.get('title') for page in image_usages if ':' not in page.get('title')]
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
  return guessed_article.title, len(common_links), list(common_links)
