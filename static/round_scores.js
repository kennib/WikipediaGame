Vue.filter('formatNumber', function (value) {
  if (isNaN(value))
    return value
  else
    return value.toLocaleString()
});

Vue.component('round-scores', {
  props: ['state', 'room', 'round'],
  data() {
    return {
    }
  },
  methods: {
    nextRound: function() {
      socket.emit('next round', { room: this.room, state: this.state, round: this.round.number })
    },
    wikiUrl: function(article) {
      return 'https://en.wikipedia.org/wiki/'+article
    }
  },
  template:`
  <section>
    
    <div v-if="round.question.data.answer">
      <h3>Answer</h3>
      <p v-if="round.question.data.answer.article">
        <a v-bind:href="wikiUrl(round.question.data.answer.article)" target="_blank">
          {{ round.question.data.answer.article }}
        </a>
      </p>
      <details v-if="round.question.data.answer.articles">
        <summary>
          and {{ round.question.data.answer.articles.length-1 }} other articles
        </summary>
        <ul>
          <li v-for="article in round.question.data.answer.articles">
            <a v-bind:href="wikiUrl(article)" target="_blank">{{article}}</a>
          </li>
        </ul>
      </details>
    </div>
    <h3>Scores</h3>

    <table>
      <thead>
        <tr>
          <th>Player</th>
          <th>Answer</th>
          <th>{{ round.question.data.answer.scoreType }}</th>
          <th>Round Score</th>
          <th>Running Score</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="result in round.results">
          <td>{{ result.player }}</td>
          <td>
            {{ result.answer }}
            <br/>
            <a v-if="result.article" 
              v-bind:href="result.article.url" target="_blank">
              {{ result.article.title }}
            </a>
          </td>
          <td>
            <details>
              <summary>
                {{ result.score | formatNumber }} {{ round.question.data.answer.units }}
              </summary>
              <ul v-if="round.question.data.answer.units == 'links'">
                <li v-for="article in result.details">
                  <a v-bind:href="wikiUrl(article)" target="_blank">
                    {{ article }}
                  </a>
                </li>
              </ul>
              <p v-else>{{ result.details }}</p>
            </details>
          </td>
          <td>{{ result.normalised_score }}</td>
          <td>{{ result.running_score }} </td>
        </tr>
      </tbody>
    </table>
    <button v-on:click="nextRound">Next Round</button>
  </section>
  `
})