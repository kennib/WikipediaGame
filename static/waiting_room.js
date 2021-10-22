Vue.component('waiting-room', {
  props: ['players', 'buttonEvent'],
  data() {
    return {
    }
  },
  template: `
  <div>
    <h2>Players</h2>
    <ol>
      <li v-for="player in players" v-text="player"></li>
    </ol>
    <button v-on:click="buttonEvent">Start Game</button>
  </div>
    `
})