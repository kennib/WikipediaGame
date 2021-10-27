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
    <input v-model="player" v-on:keyup.enter="onSubmit(player)" />
    <input type="submit" v-on:click="onSubmit(player)" />
  </div>`
})