Vue.component('waiting-room', {
  props: ['state', 'room', 'players'],
  data() {
    return {
    }
  },
  methods: {
    nextRound: function() {
      socket.emit('next round', { room: this.room, state: this.state })
    },
  },
  template: `
  <div>
    <h2>Players</h2>
    <ol>
      <li v-for="player in players" v-text="player"></li>
    </ol>
    <button v-on:click="nextRound">Start Game</button>
  </div>
    `
})