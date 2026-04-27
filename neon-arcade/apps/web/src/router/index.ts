import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Game from '../views/Game.vue'
import Admin from '../views/Admin.vue'
import Profile from '../views/Profile.vue'
import Leaderboard from '../views/Leaderboard.vue'
import Novel from '../views/Novel.vue'
import Match3Endless from '../games/Match3Endless.vue'
import Match3Home from '../games/Match3Home.vue'
import Match3Levels from '../games/Match3Levels.vue'
import Match3Level from '../games/Match3Level.vue'
import Match3Shop from '../games/Match3Shop.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/profile',
      name: 'profile',
      component: Profile
    },
    {
      path: '/leaderboard',
      name: 'leaderboard',
      component: Leaderboard
    },
    {
      path: '/game/:id',
      name: 'game',
      component: Game
    },
    {
      path: '/game/match3',
      name: 'match3',
      component: Match3Home
    },
    {
      path: '/game/match3-endless',
      name: 'match3-endless',
      component: Match3Endless
    },
    {
      path: '/game/match3-levels',
      name: 'match3-levels',
      component: Match3Levels
    },
    {
      path: '/game/match3-level/:id',
      name: 'match3-level',
      component: Match3Level
    },
    {
      path: '/game/match3-shop',
      name: 'match3-shop',
      component: Match3Shop
    },
    {
      path: '/admin',
      name: 'admin',
      component: Admin
    },
    {
      path: '/novel',
      name: 'novel',
      component: Novel
    }
  ]
})

export default router
