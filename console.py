import re
import wiki

def choose_option(name, options):
  for i, option in enumerate(options):
    print(f'{i}) {option}')
  choice = int(input(f'Choose a {name}: '))
  return options[choice]

def choose_random_article():
  articles = wiki.get_random_articles()
  print(articles)
  article = wiki.get_article(choose_option('article', articles))
  print(article.title)
  print(article.summary[:250])
  return article

def choose_article(article_title):
  try:
    article = wiki.get_article(article_title)
  except wiki.DisambiguationError as e:
    choice = choose_option('article', e.options)
    article = wiki.get_article(choice)
  return article

def guess_article_with_most_words(word):
  article_title = get_answer(f'Find the page with the most {word}: ', [word])

  _, matches = wiki.get_article_wordcount(article_title, word)
  article = wiki.get_article(article_title)

  print(f'The {article.title} article has {matches} {word}s')

  if matches:
    print(wiki.context(word, article))

  return matches

def guess_article_with_most_common_links(article):
  article_title = get_answer(f'Find the page with the common links with {article.title}: ', article.title.split())
  guessed_article = wiki.get_article(article_title)

  common_links = set(article.links) & set(guessed_article.links)

  print(f'The {guessed_article.title} article has {len(common_links)} links in common with {article.title}')
  print(common_links)

  return len(common_links)

def guess_article_with_most_views(date):
  year, month = date
  article_title = get_answer(f'Find the most popular article for {month}/{year}: ')
  article = wiki.get_article(article_title)
  
  pageviews = wiki.get_pageviews(article.title.replace(' ', '_'), date)

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

def game():
  print('Round 1')
  round(wiki.get_random_word, guess_article_with_most_words)
  print()
  print('Round 2')
  round(choose_random_article, guess_article_with_most_common_links)
  print()
  print('Round 3')
  round(wiki.get_random_month, guess_article_with_most_views)