Vue.component('final-scores', {
  props: ['results', 'buttonEvent'],
  data() {
    return {
    }
  },
  template: `
  <div>
    <h2>Final scores</h2>
    <table>
      <thead>
        <tr>
          <th>Player</th>
          <th>Score</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(result, index) in results">
          <td>{{ result.player }}</td>
          <td>{{ result.score }}</td>
          <td v-if="index==0">Winner!</td>
        </tr>
      </tbody>
    </table>
    <button v-on:click="buttonEvent">Play again</button>
  </div>
  `
})