from flask import Flask, render_template, request, send_from_directory, redirect, make_response
from flask_socketio import SocketIO, emit, join_room
import wiki
from game import Room, generate_room_code
from rounds import InvalidAnswerError

app = Flask(__name__)
socketio = SocketIO(app)

rooms = {}

@app.route('/')
def home():
  return render_template('home.html')

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
  return send_from_directory('templates', 'room.html')

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

@socketio.on('next round')
def next_round(data):
  room_code = data['room']
  room = rooms[room_code]
  
  if data['state'] == room.state and room.state == 'waiting room' or data['round'] == room.round_number:
    room.next_round()
    print('update state', room.current_state())
    emit('update state', room.current_state(), json=True, broadcast=True, room=room_code)

    print('round begin')

    this_round = room.round
    socketio.sleep(room.round_time)
    print('round end')

    if room.state == 'round' and room.round == this_round:
      room.score_round()
      emit('update state', room.current_state(), json=True, broadcast=True, room=room_code)

@socketio.on('send answer')
def send_answer(data):
  room_code = data['room']
  room = rooms[room_code]

  try:
    room.receive_answer(data['player'], data['answer'])
    emit('update state', room.current_state(data['player']), json=True)
    emit('update state', {'waitingFor': room.waiting_for_players()}, json=True, broadcast=True, room=room_code)
  except wiki.DisambiguationError as e:
    emit('disambiguation', {'word': data['answer'], 'options': e.options})
  except InvalidAnswerError as e:
    emit('invalid answer', {'answer': data['answer'], 'message': str(e)})
  
  if room.round_complete():
    room.score_round()
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

if __name__ == '__main__':
  #console.game()
  socketio.run(app, host='0.0.0.0')