import os
import json

import redis
import fakeredis

from game import Room

REDIS_URL = os.environ.get('REDIS_URL')

if REDIS_URL:
  r = redis.Redis.from_url(REDIS_URL)
else:
  r = fakeredis.FakeStrictRedis()

def save_rooms(rooms):
  r.set('rooms', json.dumps(rooms))

def load_rooms():
  rooms_json = r.get('rooms')
  rooms_data = json.loads(rooms_json)

  rooms = {
    room_code: Room.from_dict(room)
    for room_code, room in rooms_data.items()
  }

  return rooms

def save_room(room):
  r.set(f'room: {room.code}', room.to_JSON())

def load_room(room_code):
  room_json = r.get(f'room: {room_code}')
  room = Room.from_JSON(room_json)

  return room