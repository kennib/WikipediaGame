Vue.component('round-setup', {
  props: ['room', 'player', 'round'],
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
    <div v-if="round.playerChoice.player == player">
      <h3>Select an article</h3>
      <div class="options">
        <button v-for="option in round.playerChoice.options"
          v-on:click="choose(option)">
          {{ option }}
        </button>
      </div>
    </div>
    <div v-else>
      {{ round.playerChoice.player }} is choosing an article
    </div>
  </div>
  `
})