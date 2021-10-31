Vue.component('timer', {
  props: ['duration', 'startTime'],
  data() {
    return {
      enabled: true,
      time: this.startTime || this.duration,
    }
  },
  methods: {
    timeFormatted: function() {
      return (this.time/this.duration*100)+'%'
    }
  },
  watch: {
    enabled(value) {
      if (value) {
        setTimeout(() => {
          this.time--
        }, 1000);
      }
    },
    time: {
      handler(value) {
        if (value > 0 && this.enabled) {
          setTimeout(() => {
            this.time--
          }, 1000);
        }
      },
      immediate: true // This ensures the watcher is triggered upon creation
    },
  },
  template: `
<div class="timer">
  <div class="time"
       v-bind:style="{width: timeFormatted()}">
    {{ time }} seconds
  </div>
</div>`,
})