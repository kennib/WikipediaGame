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
    },
    choose: function(choice) {
      this.playerSelection = choice
      this.submitPlayerChoice()
    },
  },
  template: `
  <div>
    <div v-if="playerChoice.player == player">
      <h3>Select an article</h3>
      <div class="options">
        <button v-for="option in playerChoice.options"
          v-on:click="choose(option)">
          {{ option }}
        </button>
      </div>
    </div>
    <div v-else>
      {{ playerChoice.player }} is choosing an article
    </div>
  </div>
  `
})