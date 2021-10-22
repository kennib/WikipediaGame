Vue.component('round-setup', {
  props: ['playerChoice', 'player', 'room'],
  data() {
    return {
      playerSelection: '',
    }
  },
  methods: {
    submitPlayerChoice: function() {
      socket.emit('send player choice', { room: this.room, choice: this.playerSelection })
    }
  },
  template: `
  <div>
    <div v-if="playerChoice.player == player">
      Select an article
      <select v-model="playerSelection" v-on:change="submitPlayerChoice">
        <option></option>
        <option v-for="option in playerChoice.options" v-bind:value="option">
          {{ option }}
        </option>
      </select>
    </div>
    <div v-else>
      {{ playerChoice.player }} is choosing an article
    </div>
  </div>
  `
})