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

def delete_rooms():
  r.delete('room')

def save_rooms(rooms):
  for room in rooms.values():
    save_room(room)

def load_rooms():
  rooms_dict = r.hgetall('room')

  rooms_dict = {
    room_code.decode(): Room.from_JSON(room) 
    for room_code, room in rooms_dict.items()
  }

  return rooms_dict

def delete_room(room):
  r.hdel('room', room.code)

def save_room(room):
  r.hset('room', room.code, room.to_JSON())

def load_room(room_code):
  room_json = r.hget('room', room_code)
  room = Room.from_JSON(room_json)

  return room