Vue.component('round-answer', {
  props: ['room', 'player', 'round', 'question', 'roundTime', 'disambiguation', 'submitted', 'waitingFor', 'invalidAnswer'],
  data() {
    return {
      answer: '',
      answerState: 'need answer',
    }
  },
  methods: {
    submitAnswer: function() {
      if (this.answer) {
        socket.emit('send answer', { room: this.room, player: this.player, answer: this.answer })
        this.answerState = 'processing answer'
      }
    },
    chooseAnswer: function(option) {
      this.answer = option
      this.submitAnswer()
    },
  },
  watch: {
    submitted: function(submitted) {
      if (submitted) {
        this.answerState = 'valid answer'
      }
    },
  },
  template: `
  <div>
    <timer v-bind:count-down="roundTime"></timer>
    <h2>Round {{ round }}</h2>
    <h3 v-text="question.description"></h3>
    <p v-if="question.data.image">
      <img v-bind:src="question.data.image" />
    </p>

    <div v-if="disambiguation">
      Which {{ disambiguation.word }} did you mean?
      <ul>
        <li v-for="option in disambiguation.options">
          <a v-on:click="chooseAnswer(option)" href="javascript:undefined">
            {{ option }}
          </a>
        </li>
      </ul>
    </div>

    <div v-else-if="answerState == 'need answer'">
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

    <div v-else-if="answerState == 'processing answer'">
      Evaluating your answer...
    </div>

    <div v-else-if="answerState == 'valid answer'">
      Waiting for
      <em v-if="waitingFor.length == 1">{{ waitingFor[0] }}</em>
      <em v-else>{{ waitingFor.length }} players</em>
      to enter an answer
    </div>
  </div>`
})