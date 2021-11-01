Vue.component('round', {
  props: ['state', 'room', 'player', 'round', 'syncTime'],
  data() {
    return {
    }
  },
  template: `
  <div>
    <h2>
      {{ round.title }}
      <small>
        Round {{ round.number }}
      </small>
    </h2>

    <section v-if="state == 'round' || state == 'round scores'">
      <h3>Question</h3>
      <p v-text="round.question.description"></p>
      <p v-if="round.question.data.image">
        <img v-bind:src="round.question.data.image" />
      </p>
    </section>

    <round-setup v-if="state == 'round setup'"
      v-bind:room="room"
      v-bind:player="player"
      v-bind:round="round"
     />

    <round-answer v-if="state == 'round'"
      v-bind:room="room"
      v-bind:player="player"
      v-bind:round="round"
      v-bind:sync-time="syncTime"
     />

    <round-scores v-if="state == 'round scores'"
      v-bind:state="state"
      v-bind:room="room"
      v-bind:player="player"
      v-bind:round="round"
     />
  </div>`
})