import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import ViewSearchResult from '../views/ViewSearchResult.vue'

import About from '../views/About.vue'


Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/searchresult/:id',
    name: 'ViewSearchResult',
    component: ViewSearchResult
  },
  {
    path: '/about',
    name: 'About',
    component: About
  },

]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
