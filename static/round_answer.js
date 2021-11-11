Vue.component('round-answer', {
  props: ['room', 'player', 'round', 'syncTime'],
  data() {
    return {
      active: false,
      answer: '',
      answerState: 'need answer',
      roundFinished: false,
    }
  },
  beforeCreate: function() {
    let vm = this
    socket.on('disambiguation', function(disambiguation) {
      vm.round.submitted = false
      console.log(disambiguation)
      vm.answerState = 'need answer'
      vm.round.disambiguation = disambiguation
    })
    socket.on('invalid answer', function(invalidAnswer) {
      vm.round.submitted = false
      console.log(invalidAnswer)
      vm.round.invalidAnswer = invalidAnswer.message
      vm.answerState = 'need answer'
    })
  },
  methods: {
    submitAnswer: function() {
      if (this.answer) {
        socket.emit('send answer', { room: this.room, player: this.player, answer: this.answer })
        this.answerState = 'processing answer'
      }
    },
    chooseAnswer: function(option) {
      this.round.disambiguation = undefined
      this.answer = option
      this.submitAnswer()
    },
    tryAgain: function() {
      this.round.disambiguation = undefined
      this.answer = ''
    },
    timeLeft: function() {
      let now = Math.floor(Date.now() / 1000)
      let duration = this.round.finishTime - now - this.syncTime
      return duration
    },
    roundFinish: function() {
      this.roundFinished = true
      if (this.active) {
        this.submitAnswer()
      } else {
        this.$emit('inactive')
      }
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
  <section>
    <h3>Enter your answer</h3>

    <timer
      v-bind:duration="round.time"
      v-bind:start-time="timeLeft()"
      v-on:finish="roundFinish()" />

    <div v-if="answerState == 'need answer'">
      <div v-if="round.invalidAnswer">
        {{ round.invalidAnswer }}
      </div>
      <div v-if="round.disambiguation">
        <p>Which <em>{{ round.disambiguation.word }}</em> did you mean?</p>
        <ul>
          <li v-for="option in round.disambiguation.options">
            <a v-on:click="chooseAnswer(option)" href="javascript:undefined">
              {{ option }}
            </a>
          </li>
          <br/>
          <button v-on:click="tryAgain()">
            Try another word
          </button>
        </ul>
      </div>
      <form v-else v-on:submit.prevent>
        <p>
          <label for="answer">Answer</label>
          <input name="answer"
            v-model="answer"
            v-on:keydown="active = true"
            v-on:keyup.enter="submitAnswer"
            v-bind:disabled="roundFinished"
            autocomplete="off"/>
        </p>
        <button v-on:click="submitAnswer"
          v-bind:disabled="roundFinished">
            Submit answer
        </button>
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
  </section>`
})