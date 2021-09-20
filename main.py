import wikipedia
import re
import random

words = open('words.txt').readlines()
word = random.choice(words).strip()
print(word)

def guess_article(word):
  article_title = input(f'Find the page with the most {word}: ')

  search = wikipedia.search(article_title)
  article = wikipedia.page(search[0], auto_suggest=False)

  matches = re.findall(word, article.content, re.IGNORECASE)

  print(f'The {article.title} article has {len(matches)} {word}s')

  return len(matches)


player1 = guess_article(word)
player2 = guess_article(word)

if player1 > player2:
  print('Player 1 wins!')
elif player1 < player2:
  print('Player 2 wins!')
else:
  print('It\'s a draw!')