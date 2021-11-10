import pytest
from unittest.mock import MagicMock, patch

import sys
import os
from copy import copy

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import rounds
from game import Room
from persistence import delete_rooms, save_rooms, load_rooms, delete_room, save_room, load_room

def test_save_load_room():
  room_code = 'test room'
  room = Room(room_code)

  delete_rooms()
  save_room(room)
  loaded_room = load_room(room_code)

  assert loaded_room == room

def test_save_load_rooms():
  room = Room('', rounds=[rounds.HighestWordCountRound])

  rooms = {}
  for room_index in range(10):
    room_code = 'ROOM'+str(room_index)
    rooms[room_code] = copy(room)
    rooms[room_code].code = room_code

  delete_rooms()
  save_rooms(rooms)
  rooms_loaded = load_rooms()

  assert rooms_loaded == rooms

def test_delete_room():
  room = Room('', rounds=[rounds.HighestWordCountRound])

  rooms = {}
  for room_index in range(10):
    room_code = 'ROOM'+str(room_index)
    rooms[room_code] = copy(room)
    rooms[room_code].code = room_code

  delete_rooms()
  save_rooms(rooms)

  deleted_room_code = 'ROOM3'
  delete_room(rooms[deleted_room_code])
  del rooms[deleted_room_code]

  rooms_loaded = load_rooms()

  assert deleted_room_code not in rooms_loaded
  assert rooms_loaded == rooms