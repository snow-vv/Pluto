import Vue from 'vue'
import Router from 'vue-router'
import store from '@/store'
import routes from './routes.js'

Vue.use(Router)

const router = new Router({
  routes
})

export default router
