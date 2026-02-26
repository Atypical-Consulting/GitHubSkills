import DefaultTheme from 'vitepress/theme'
import Badge from './components/Badge.vue'
import StepFlow from './components/StepFlow.vue'
import HomeContent from './components/HomeContent.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('Badge', Badge)
    app.component('StepFlow', StepFlow)
    app.component('HomeContent', HomeContent)
  },
}
