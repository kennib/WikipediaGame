Vue.component('round-setup', {
  props: ['room', 'player', 'round'],
  data() {
    return {
      playerSelection: undefined,
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
  <section>
    <h3>Choose an article</h3>

    <div v-if="round.playerChoice.player == player">
      <div v-if="playerSelection == undefined" class="options">
        <button v-for="option in round.playerChoice.options"
          v-on:click="choose(option)">
          {{ option }}
        </button>
      </div>
      <div v-else>
        You chose 
        <em>{{playerSelection}}</em>
      </div>
    </div>
    <div v-else>
      {{ round.playerChoice.player }} is choosing an article
    </div>
  </section>
  `
})
