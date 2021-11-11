Vue.component('timer', {
  props: ['duration', 'startTime'],
  data() {
    let time = this.startTime || this.duration
    return {
      enabled: time > 0,
      time: time,
      start: new Date().valueOf()/1000 + (this.startTime || 0) - (this.duration || 0),
      end: new Date().valueOf()/1000 + (this.startTime || 0),
    }
  },
  methods: {
    timeFormatted: function() {
      return (this.time/this.duration*100)+'%'
    },
    countdown: function() {
      let vm = this
      if (vm.time > 0 && vm.enabled) {
        setTimeout(function() {
          vm.time = Math.floor(vm.end - new Date().valueOf()/1000)
          vm.$forceUpdate()
        }, 1000);
      } else if (vm.time <= 0 && vm.enabled) {
        vm.enabled = false
        vm.$emit('finish')
      }
    },
  },
  watch: {
    enabled: function() { 
      this.countdown()
    },
    time: {
      handler: function() {
        this.countdown()
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