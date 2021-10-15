from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit
import wiki
from game import Room

app = Flask(__name__)
socketio = SocketIO(app)

rooms = {}

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/room', methods=['GET'])
def room():
  room_code = request.args.get('room')
  player = request.args.get('name')
  room = rooms.get(room_code, Room(room_code))
  rooms[room_code] = room
  return send_from_directory('templates', 'room.html')

@socketio.on('join')
def join(data):
  room_code = data['room']
  player = data['player']
  room = rooms.get(room_code, Room(room_code))
  rooms[room_code] = room
  room.add_player(player)
  emit('new players', list(room.players), json=True, broadcast=True)
  emit('update state', room.current_state(player), json=True)

@socketio.on('next round')
def next_round(data):
  room_code = data['room']
  room = rooms[room_code]
  
  if data['state'] == room.state and room.state == 'waiting room' or data['round'] == room.round_number:
    room.next_round()
    print('update state', room.current_state())
    emit('update state', room.current_state(), json=True, broadcast=True)

    print('round begin')

    this_round = room.round
    socketio.sleep(room.round_time)
    print('round end')

    if room.state == 'round' and room.round == this_round:
      room.score_round()
      emit('update state', room.current_state(), json=True, broadcast=True)

@socketio.on('send answer')
def send_answer(data):
  room = rooms[data['room']]

  try:
    room.receive_answer(data['player'], data['answer'])
    emit('update state', room.current_state(data['player']), json=True)
    emit('update state', {'waitingFor': room.waiting_for_players()}, json=True, broadcast=True)
  except wiki.DisambiguationError as e:
    emit('disambiguation', {'word': data['answer'], 'options': e.options})
  
  if room.round_complete():
    room.score_round()
    emit('update state', room.current_state(), json=True, broadcast=True)

@socketio.on('play again')
def play_again(data):
  room_code = data['room']
  players = rooms[room_code].players
  rooms[room_code] = room = Room(room_code)
  
  for player in players:
    room.add_player(player)

  emit('update state', room.current_state(), json=True, broadcast=True)

@socketio.on('send player choice')
def handle_player_choice(data):
  room = rooms[data['room']]
  article_title = data['choice']
  room.setup_round(article_title)
  emit('update state', room.current_state(), json=True, broadcast=True)

if __name__ == '__main__':
  #console.game()
  socketio.run(app, host='0.0.0.0')