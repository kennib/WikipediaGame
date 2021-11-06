import wiki

STOPWORDS = open('data/stopwords.txt').read().splitlines()

class InvalidAnswerError(Exception):
  pass

class Score():
  def __init__(self, article_title, raw_score, display_score=None, details=None):
    if article_title:
      self.article = wiki.get_article(article_title)
    else:
      self.article = None
    self.raw_score = raw_score
    self.display_score = display_score
    self.details = details

class Round():
  def __init__(self):
    self.title = ''
    self.article = None
    self.question = ''
    self.data = {}
    self.invalid_words = []

  def score(self, answer):
    raise Exception('Not implemented')

  def validate_answer(self, answer):
    answer_words = answer.lower().strip().split()

    if set(answer_words) & set(self.invalid_words) \
      or any(word in invalid or invalid in word for invalid in self.invalid_words for word in answer_words):
        raise InvalidAnswerError('You can\'t use a word from the question!')
    else:
      return True

class HighestWordCountRound(Round):
  def __init__(self):
    self.title = 'Article word count round'
    self.word = wiki.get_random_word()
    self.invalid_words = [self.word.lower()]
    self.question = f'Which page has the most {self.word}?'
    self.data = {
      'answer': {
        'scoreType': 'Word count',
        'units': self.word,
      }
    }

  def score(self, answer):
    article = wiki.get_article(answer)
    raw_score = wiki.get_article_wordcount(article, self.word)
    score = Score(article.title, raw_score)
    if raw_score:
      context = wiki.context(self.word, article)
      score.details = context
    return score

class MostCommonLinksRound(Round):
  def __init__(self):
    self.title = 'Most common links round'
    self.article_title = ''
    self.question = 'Find the article with the most common links with '
    self.invalid_words = []
    self.data = {
      'answer': {
        'scoreType': 'Link count',
        'units': 'links',
      }
    }

  def setup(self, article_title):
    article = wiki.get_article(article_title)
    self.data['article'] = {
      'title': article_title,
      'summary': wiki.summarise(article),
      'url': article.url,
    }
    self.article_title = article_title
    self.invalid_words = article_title.lower().split()

  def score(self, answer):
    article_title, raw_score, links =  wiki.get_common_links(self.article_title, answer)
    score = Score(article_title, raw_score)
    score.details = links
    return score

class MostViewsRound(Round):
  def __init__(self):
    self.title = 'Most popular article round'
    self.year, self.month = wiki.get_random_month()
    self.word = wiki.get_random_word()
    self.invalid_words = [self.word.lower()]
    self.question = f'Find the most popular article for {self.month}/{self.year} which contains {self.word}'
    self.data = {
      'answer': {
        'scoreType': 'View count',
        'units': 'views',
      }
    }

  def score(self, answer):
    article = wiki.get_article(answer)
    views = wiki.get_pageviews(article.title.replace(' ', '_'), (self.year, self.month))
    word_in_article = self.word.lower() in article.content.lower().split()
    raw_score = views if word_in_article else 0
    display_score = views
    details = f'{views:,} views and {self.word} {"does" if word_in_article else "does not"} appear in the article'

    score = Score(article.title, raw_score, display_score, details)
    return score

class ImageRound(Round):
  def __init__(self):
    self.title = 'The image round'
    
    image_url = None
    while not image_url:
      try:
        self.image, image_url, self.article = wiki.get_random_image()
      except wiki.NoImageError:
        pass
    
    self.articles = wiki.get_pages_containing_image(self.image)
    self.question = f'Find an article containing the following image'
    self.data = {
      'image': image_url,
      'answer': {
        'article': self.article.title,
        'articles': self.articles,
        'scoreType': 'Results'
      }
    }
    self.invalid_words = []
  
  def score(self, answer):
    article = wiki.get_article(answer)
    
    if article.title in self.articles:
      display_score, raw_score = 'Correct article', 10
      details = 'Your article contains the image'
    elif set(article.links) & set(self.articles):
      display_score, raw_score = 'Links to article', 7
      details = 'Your article links to an article containing the image'
    elif article.title in self.article.links:
      display_score, raw_score = 'Linked from article', 5
      details = 'Your article is linked to by an article containing the image'
    else:
      display_score, raw_score = 'Incorrect article', 0
      details = 'Your article does not contain the image'

    score = Score(article.title, raw_score, display_score, details)
    return score

class MostFrequentWordRound(Round):
  def __init__(self):
    self.title = 'Highest word count round'
    self.article_title = ''
    self.question = 'Guess the most common word in the article for '
    self.data = {
      'answer': {
        'scoreType': 'Word count',
        'units': 'words',
      }
    }
    self.invalid_words = []
  
  def setup(self, article_title):
    article = wiki.get_article(article_title)
    self.data['article'] = {
      'title': article_title,
      'summary': wiki.summarise(article),
      'url': article.url,
    }
    self.article_title = article_title
    self.article = article
    self.invalid_words = article_title.lower().split()

  def score(self, answer):
    raw_score = wiki.get_article_wordcount(self.article, answer)
    if raw_score:
      self.data['answer']['article word count'] = raw_score
    score = Score(None, raw_score)
    if raw_score:
      context = wiki.context(answer, self.article)
      score.details = context
    return score
  
  def validate_answer(self, answer):
    answer = answer.lower().strip()
    
    if answer in STOPWORDS:
      raise InvalidAnswerError('Your word is too common, try a little harder!')
    else:
      return super().validate_answer(answer)

ROUNDS = [
  HighestWordCountRound,
  MostCommonLinksRound,
  ImageRound,
  MostFrequentWordRound,
  MostViewsRound
]