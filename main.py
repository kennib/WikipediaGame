from flask import Flask, send_from_directory, render_template, request, redirect, make_response
from flask_socketio import SocketIO, emit, join_room

import os

import wiki
from game import Room, generate_room_code
from rounds import InvalidAnswerError

from analytics import record_game_start, record_game_completed, get_stats
import persistence as db

app = Flask(__name__)
socketio = SocketIO(app)

rooms = {}


favicon_path = os.path.join(app.root_path, 'static/favicon')
@app.route('/android-chrome-512x512.png')
@app.route('/android-chrome-192x192.png')
@app.route('/favicon-16x16.png')
@app.route('/favicon-32x32.png')
@app.route('/apple-touch-icon.png')
@app.route('/favicon.ico')
def favicon():
  favicon_file = request.path[1:]
  return send_from_directory(favicon_path,
    favicon_file, mimetype='image/x-icon')

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/stats')
def stats():
  stats = get_stats()
  return render_template('stats.html', **stats)

@app.route('/room', methods=['GET'])
def join_a_room():
  room_code = request.args.get('room') or generate_room_code(exclude=rooms.keys())
  room_code = room_code.upper()

  room = rooms.get(room_code, Room(room_code))
  rooms[room_code] = room

  player = request.args.get('name')

  response = make_response(redirect(f'/room/{room_code}'))
  response.set_cookie('player', player)

  return response

@app.route('/room/<room_code>', methods=['GET'])
def room(room_code):
  return render_template('room.html', room=room_code)

@socketio.event
def connect(data=None):
  if data:
    join(data)

@socketio.on('join')
def join(data):
  room_code = data['room']
  player = data['player']
  
  room = rooms.get(room_code, Room(room_code))
  rooms[room_code] = room
  room.add_player(player)

  join_room(room_code)
  emit('new players', list(room.players), json=True, broadcast=True, room=room_code)
  emit('update state', room.current_state(player), json=True)


@socketio.on('leave')
def data(data):
  room_code = data['room']
  player = data['player']
  
  room = rooms.get(room_code, Room(room_code))
  rooms[room_code] = room
  room.remove_player(player)
  
  emit('new players', list(room.players), json=True, broadcast=True, room=room_code)

@socketio.on('next round')
def next_round(data):
  room_code = data['room']
  room = rooms[room_code]
  
  if data['state'] == room.state and room.state == 'waiting room' or data['round'] == room.round_number:
    if room.state == 'waiting room':
      record_game_start(len(room.players))

    room.next_round()
    emit('update state', room.current_state(), json=True, broadcast=True, room=room_code)

    if room.state == 'final scores':
      record_game_completed(len(room.players))
      db.delete_room(room)

    this_round = room.round
    socketio.sleep(room.round_time)

    if room.state == 'round' and room.round == this_round:
      room.score_round()
      db.save_room(room)
      emit('update state', room.current_state(), json=True, broadcast=True, room=room_code)

@socketio.on('send answer')
def send_answer(data):
  room_code = data['room']
  room = rooms[room_code]

  try:
    room.receive_answer(data['player'], data['answer'])
    emit('update state', room.current_state(data['player']), json=True)
    emit('partial update state', {'round': {'waitingFor': room.waiting_for_players()}}, json=True, broadcast=True, room=room_code)
  except wiki.DisambiguationError as e:
    emit('disambiguation', {'word': data['answer'], 'options': e.options})
  except InvalidAnswerError as e:
    emit('invalid answer', {'answer': data['answer'], 'message': str(e)})
  except wiki.NoArticleError as e:
    emit('invalid answer', {'answer': data['answer'], 'message': str(e)})
  
  if room.round_complete():
    room.score_round()
    db.save_room(room)
    emit('update state', room.current_state(), json=True, broadcast=True, room=room_code)

@socketio.on('play again')
def play_again(data):
  room_code = data['room']
  players = rooms[room_code].players
  rooms[room_code] = room = Room(room_code)
  
  for player in players:
    room.add_player(player)

  emit('update state', room.current_state(), json=True, broadcast=True, room=room_code)

@socketio.on('send player choice')
def handle_player_choice(data):
  room_code = data['room']
  room = rooms[room_code]
  article_title = data['choice']
  room.setup_round(article_title)
  emit('update state', room.current_state(), json=True, broadcast=True, room=room_code)

def load_rooms():
  rooms.update(db.load_rooms())

if __name__ == '__main__':
  #console.game()
  app.before_first_request(load_rooms)
  socketio.run(app, host='0.0.0.0')