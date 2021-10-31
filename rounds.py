import wiki

STOPWORDS = open('stopwords.txt').read().splitlines()

class InvalidAnswerError(Exception):
  pass

class Score():
  def __init__(self, article_title, raw_score):
    self.article_title = article_title
    self.raw_score = raw_score
    #TODO possibly only need details?
    self.example = None 
    self.details = None

class Round():
  def __init__(self):
    self.article = None
    self.question = ''
    self.data = {}
    self.invalid_words = []

  def score(self, answer):
    raise Exception('Not implemented')

  def validate_answer(self, answer):
    answer_words = answer.strip().split()

    if set(answer_words) & set(self.invalid_words) \
      or any(word in invalid or invalid in word for invalid in self.invalid_words for word in answer_words):
        raise InvalidAnswerError('You can\'t use a word from the question!')
    else:
      return True

class HighestWordCountRound(Round):
  def __init__(self):
    self.word = wiki.get_random_word()
    self.invalid_words = [self.word]
    self.question = f'Which page has the most {self.word}?'
    self.data = {
      'answer': {
        'scoreType': 'Word count',
      }
    }

  def score(self, answer):
    article = wiki.get_article(answer)
    raw_score = wiki.get_article_wordcount(article, self.word)
    context = None
    if raw_score:
      context = wiki.context(self.word, article)
      self.data['answer']['show_example'] = True 
    score = Score(article.title, raw_score)
    score.example = context
    return score

class MostCommonLinksRound(Round):
  def __init__(self):
    self.article_title = ''
    self.question = ''
    self.invalid_words = []
    self.data = {
      'answer': {
        'scoreType': 'Link count'
      }
    }

  def setup(self, article_title):
    self.article_title = article_title
    self.invalid_words = article_title.split()
    self.question = f'Find the page with the most common links with {self.article_title}'

  def score(self, answer):
    article_title, raw_score =  wiki.get_common_links(self.article_title, answer)
    return Score(article_title, raw_score)

class MostViewsRound(Round):
  def __init__(self):
    self.year, self.month = wiki.get_random_month()
    self.word = wiki.get_random_word()
    self.invalid_words = [self.word]
    self.question = f'Find the most popular article for {self.month}/{self.year} which contains {self.word}'
    self.data = {
      'answer': {
        'scoreType': 'View count'
      }
    }

  def score(self, answer):
    article = wiki.get_article(answer)
    views = wiki.get_pageviews(article.title.replace(' ', '_'), (self.year, self.month))
    raw_score = views if self.word in article.content else 0
    self.data['answer']['wordAppears'] = ''
    return Score(article.title, raw_score)

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
    self.invalid_words = []
  
  def score(self, answer):
    article = wiki.get_article(answer)
    details = ''
    self.data['answer']['show_details'] = True 
    if article.title in self.articles:
      raw_score = 1
      details = 'Selected article contains the image'
    elif set(article.links) & set(self.articles):
      raw_score = 0.75
      details = 'Selected article links to article containing the image'
    elif article.title in self.article.links:
      raw_score = 0.5
      details = 'Selected article is linked to by article containing the image'
    else:
      raw_score = 0
      details = 'Selected article does not contain the image'
    score = Score(article.title, raw_score)
    score.details = details 
    return score

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
    if score:
      self.data['answer']['article word count'] = score
    return Score(self.article.title, score)
  
  def validate_answer(self, answer):
    answer = answer.strip()
    
    if answer in STOPWORDS:
      raise InvalidAnswerError('Your word is too common, try a little harder!')
    else:
      return True

ROUNDS = [
  HighestWordCountRound,
  MostCommonLinksRound,
  ImageRound,
  MostFrequentWordRound,
  MostViewsRound
]