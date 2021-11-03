Vue.component('timer', {
  props: ['duration', 'startTime'],
  data() {
    return {
      enabled: true,
      time: this.startTime || this.duration,
      start: new Date().valueOf()/1000 + (this.startTime || 0) - (this.duration || 0),
      end: new Date().valueOf()/1000 + (this.startTime || 0),
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
          this.time = Math.floor(this.end - new Date().valueOf()/1000)
        }, 1000);
      }
    },
    time: {
      handler(value) {
        if (value > 0 && this.enabled) {
          setTimeout(() => {
            this.time = Math.floor(this.end - new Date().valueOf()/1000)
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