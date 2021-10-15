import wiki

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