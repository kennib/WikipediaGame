Vue.component('round-scores', {
  props: ['round', 'question', 'results', 'buttonEvent'],
  data() {
    return {
    }
  },
  template:`
  <div>
    <h2>Round {{ round }} - scores</h2>
    <h3 v-text="question.description"></h3>
    <p v-if="question.data.image">
      <img v-bind:src="question.data.image" />
    </p>
    <div v-if="question.data.answer">
      <h4 v-if="question.data.answer.article">
        Article: 
        <span v-text="question.data.answer.article"></span>
      </h4>
      <h4 v-if="question.data.answer.articles">
        Answer:
        <span v-for="article in question.data.answer.articles">{{article}} </span>
      </h4>
    </div>
    <table>
      <thead>
        <tr>
          <th>Player</th>
          <th>Answer</th>
          <th>Article</th>
          <th>{{ question.data.answer.scoreType }}</th>
          <th v-if="question.data.answer.show_example">Example</th>
          <th v-if="question.data.answer.show_details">Details</th>
          <th>Round Score</th>
          <th>Running Score</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="result in results">
          <td>{{ result.player }}</td>
          <td>{{ result.answer }}</td>
          <td>{{ result.article }}</td>
          <td>{{ result.raw_score }}</td>
          <td v-if="question.data.answer.show_example">{{ result.example }}</td>
          <td v-if="question.data.answer.show_details">{{ result.details }}</td>
          <td>{{ result.normalised_score }}</td>
          <td>{{ result.running_score }} </td>
        </tr>
      </tbody>
    </table>
    <button v-on:click="buttonEvent">Next Round</button>
  </div>
  `
})