Vue.component('round-answer', {
  props: ['room', 'player', 'round'],
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
    'round.submitted': function(submitted) {
      if (submitted) {
        this.answerState = 'valid answer'
      }
    },
  },
  template: `
  <div>
    <h2>
      {{ round.title }}
      <small>
        Round {{ round.number }}
      </small>
    </h2>

    <h3>Enter your answer</h3>

    <p v-text="round.question.description"></p>
    <p v-if="round.question.data.image">
      <img v-bind:src="round.question.data.image" />
    </p>

    <timer v-bind:count-down="round.time"></timer>

    <div v-if="round.disambiguation">
      Which {{ round.disambiguation.word }} did you mean?
      <ul>
        <li v-for="option in round.disambiguation.options">
          <a v-on:click="chooseAnswer(option)" href="javascript:undefined">
            {{ option }}
          </a>
        </li>
      </ul>
    </div>

    <div v-else-if="answerState == 'need answer'">
      <div v-if="round.invalidAnswer">
        {{ round.invalidAnswer }}
      </div>
      <form v-on:submit.prevent>
        <p>
          <label for="answer">Answer</label>
          <input name="answer"
            v-model="answer"
            v-on:keyup.enter="submitAnswer"
            autocomplete="off"></input>
        </p>
        <button v-on:click="submitAnswer">Submit answer</button>
      </form>
    </div>

    <div v-else-if="answerState == 'processing answer'">
      Evaluating your answer...
    </div>

    <div v-else-if="answerState == 'valid answer'">
      Waiting for
      <em v-if="round.waitingFor.length == 1">{{ round.waitingFor[0] }}</em>
      <em v-else>{{ round.waitingFor.length }} players</em>
      to enter an answer
    </div>
  </div>`
})