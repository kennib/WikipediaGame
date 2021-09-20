import wikipedia
import re
import random

def get_random_article():
  article = get_article(wikipedia.random())
  print(article.title)
  print(article.summary[:250])
  return article

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
    for i, option in enumerate(e.options):
      print(f'{i}) {option}')
    choice = int(input('Choose a page: '))
    article = wikipedia.page(e.options[choice], auto_suggest=False)
  return article

def guess_article_with_most_words(word):
  article_title = get_answer(f'Find the page with the most {word}: ', [word])
  article = get_article(article_title)

  words =  re.sub('[^\w\d\s]', '', article.content).split()
  matches = words.count(word)

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
  context = setup()
  player1 = ask(context)
  player2 = ask(context)

  while player1 == 0 and player2 == 0:
    retry = input('Retry? Y/N: ').lower()
    if retry == 'y':
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
  round(get_random_article, guess_article_with_most_common_links)