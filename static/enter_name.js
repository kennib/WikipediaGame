Vue.component('enter-name', {
  props: ['onSubmit'],
  data() {
    return {
      player: '',
    }
  },
  template: `
  <div>
    <h3>Enter your name</h3>
    <form v-on:submit.prevent>
      <p>
        <label for="name">Player Name</label>
        <input v-model="player" name="name"
        v-on:keyup.enter="onSubmit(player)" />
      </p>
      <input type="submit" 
        v-on:click="onSubmit(player)"
        v-bind:disabled="!player"
      />
    </form>
  </div>`
})