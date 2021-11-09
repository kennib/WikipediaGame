import os
import redis
import fakeredis

REDIS_URL = os.environ.get('REDIS_URL')

if REDIS_URL:
  r = redis.Redis.from_url(REDIS_URL)
else:
  r = fakeredis.FakeStrictRedis()

r.pipeline() \
  .setnx('games started', 0) \
  .setnx('games started : players', 0) \
  .setnx('games completed', 0) \
  .setnx('games completed : players', 0) \
  .set('live games', 0) \
  .execute()

def record_game_start(number_of_players):
  r.pipeline() \
    .incr('games started', 1) \
    .incr('games started : players', number_of_players) \
    .incr('live games', 1) \
    .execute()

def record_game_completed(number_of_players):
  r.pipeline() \
    .incr('games completed', 1) \
    .incr('games completed : players', number_of_players) \
    .decr('live games', 1) \
    .execute()

def get_stats():
  pipe = r.pipeline()

  pipe \
    .get('live games') \
    .get('games completed') \
    .get('games completed : players')

  live_games, games_played, player_games_played = pipe.execute()

  return {
    'live_games': int(live_games),
    'games_played': int(games_played),
    'player_games_played': int(player_games_played),
  }