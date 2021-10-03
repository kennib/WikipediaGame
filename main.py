from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit
import wiki

app = Flask(__name__)
socketio = SocketIO(app)

rooms = {}

class Room():
  def __init__(self, room_code):
    self.code = room_code
    self.players = set()
    self.state = 'waiting room'
    self.question = None

  def add_player(self, player):
    self.players.add(player)

  def next_round(self, question, word):
    if self.state == 'waiting room':
      self.round = 0

    self.state = 'round'
    self.word = word
    self.question = question
    self.results = {}
    self.round += 1

  def receive_answer(self, player, answer):
    article_title, count = wiki.get_article_wordcount(answer, self.word)
    self.results[player] = {
      'player': player,
      'answer': answer,
      'article': article_title,
      'score': count
    }
  
  def round_complete(self):
    return len(self.results) == len(self.players)

  def score_round(self):
    self.state = 'round scores'

  def current_state(self):
    current_state = { 'state': self.state }

    if self.state == 'round':
      current_state['round'] = self.round
      current_state['question'] = self.question
    elif self.state == 'round scores':
      current_state['round'] = self.round
      current_state['question'] = self.question
      current_state['results'] = sorted(self.results.values(), key=lambda result: result['score'], reverse=True)

    return current_state

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
  print(data)
  room_code = data['room']
  player = data['player']
  room = rooms.get(room_code, Room(room_code))
  rooms[room_code] = room
  room.add_player(player)
  emit('new players', list(room.players), json=True, broadcast=True)
  emit('update state', room.current_state(), json=True)

@socketio.on('request start')
def request_start(data):
  room_code = data['room']
  room = rooms[room_code]
  word = wiki.get_random_word()
  room.next_round(f'Which page has the most {word}?', word)
  emit('update state', room.current_state(), json=True, broadcast=True)

@socketio.on('next round')
def next_round(data):
  room_code = data['room']
  room = rooms[room_code]
  word = wiki.get_random_word()
  room.next_round(f'Which page has the most {word}?', word)
  emit('update state', room.current_state(), json=True, broadcast=True)

@socketio.on('send answer')
def send_answer(data):
  room = rooms[data['room']]
  room.receive_answer(data['player'], data['answer'])
  if room.round_complete():
    room.score_round()
    emit('update state', room.current_state(), json=True, broadcast=True)

if __name__ == '__main__':
  #console.game()
  socketio.run(app, host='0.0.0.0')