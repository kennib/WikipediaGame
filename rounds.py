import wiki

class Round():
  def __init__(self):
    self.question = ''
    self.data = {}

  def score(self, answer):
    raise Exception('Not implemented')


class HighestWordCountRound(Round):
  def __init__(self):
    self.word = wiki.get_random_word()
    self.question = f'Which page has the most {self.word}?'
    self.data = {
      'answer': {
        'scoreType': 'Word count',
      }
    }

  def score(self, answer):
    article = wiki.get_article(answer)
    score = wiki.get_article_wordcount(article, self.word)
    if score:
      context = wiki.context(answer, article)
      self.data['answer']['example'] = context if context else 'Failed to find example sentence.'
    return article.title, score

class MostCommonLinksRound(Round):
  def __init__(self):
    self.article_title = ''
    self.question = ''
    self.data = {
      'answer': {
        'scoreType': 'Link count'
      }
    }

  def setup(self, article_title):
    self.article_title = article_title
    self.question = f'Find the page with the most common links with {self.article_title}'

  def score(self, answer):
    return wiki.get_common_links(self.article_title, answer)

class MostViewsRound(Round):
  def __init__(self):
    self.year, self.month = wiki.get_random_month()
    self.word = wiki.get_random_word()
    self.question = f'Find the most popular article for {self.month}/{self.year} which contains {self.word}'
    self.data = {
      'answer': {
        'scoreType': 'View count'
      }
    }

  def score(self, answer):
    article = wiki.get_article(answer)
    views = wiki.get_pageviews(article.title.replace(' ', '_'), (self.year, self.month))
    score = views if self.word in article.content else 0
    return article.title, score

class ImageRound(Round):
  def __init__(self):
    self.image, image_url, self.article = wiki.get_random_image()
    self.articles = wiki.get_pages_containing_image(self.image)
    self.question = f'Find an article containing the following image'
    self.data = {
      'image': image_url,
      'answer': {
        'article': self.article.title,
        'articles': self.articles,
        'scoreType': 'Raw score'
      }
    }
  
  def score(self, answer):
    article = wiki.get_article(answer)
    if article.title in self.articles:
      score = 1
    elif set(article.links) & set(self.articles):
      score = 0.75
    elif article.title in self.article.links:
      score = 0.5
    else:
      score = 0
    return article.title, score

class MostFrequentWordRound(Round):
  def __init__(self):
    self.article_title = ''
    self.question = ''
    self.data = {
      'answer': {
        'scoreType': 'Word count'
      }
    }
  
  def setup(self, article_title):
    self.article_title = article_title
    self.article = wiki.get_article(self.article_title)
    self.question = f'Guess the which word appears the most in {self.article_title}'

  def score(self, answer):
    score = wiki.get_article_wordcount(self.article, answer)
    return self.article.title, score

ROUNDS = [
  HighestWordCountRound,
  MostCommonLinksRound,
  ImageRound,
  MostFrequentWordRound,
  MostViewsRound
]