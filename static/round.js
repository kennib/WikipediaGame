Vue.component('round-answer', {
  props: ['room', 'player', 'round', 'question', 'roundTime', 'disambiguation', 'submitted', 'waitingFor', 'invalidAnswer'],
  data() {
    return {
      answer: '',
    }
  },
  methods: {
    submitAnswer: function() {
      if (this.answer) {
        socket.emit('send answer', { room: this.room, player: this.player, answer: this.answer })
        this.submitted = true
      }
    },
  },
  template: `
  <div>
    <timer v-bind:count-down="roundTime"></timer>
    <h2>Round {{ round }}</h2>
    <h3 v-text="question.description"></h3>
    <img v-if="question.data.image" v-bind:src="question.data.image" />

    <div v-if="disambiguation">
      Which {{ disambiguation.word }} did you mean?
      <select v-model="answer" v-on:change="submitAnswer">
        <option></option>
        <option v-for="option in disambiguation.options" v-bind:value="option">
          {{ option }}
        </option>
      </select>
    </div>

    <div v-else-if="!submitted">
      <div v-if="invalidAnswer">
        {{ invalidAnswer }}
      </div>
      <form>
        <p>
          <label for="answer">Answer</label>
          <input name="answer"
            v-model="answer"
            v-on:keyup.enter="submitAnswer"></input>
        </p>
        <button v-on:click="submitAnswer">Submit answer</button>
      </form>
    </div>

    <div v-else>
      Waiting for
      <em v-if="waitingFor.length == 1">{{ waitingFor[0] }}</em>
      <em v-else>{{ waitingFor.length }} players</em>
      to enter an answer
    </div>
  </div>`
})