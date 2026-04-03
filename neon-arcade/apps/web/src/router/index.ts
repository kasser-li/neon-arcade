import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Game from '../views/Game.vue'
import Admin from '../views/Admin.vue'
import Match3Endless from '../games/Match3Endless.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/game/:id',
      name: 'game',
      component: Game
    },
    {
      path: '/game/match3-endless',
      name: 'match3-endless',
      component: Match3Endless
    },
    {
      path: '/admin',
      name: 'admin',
      component: Admin
    }
  ]
})

export default router
