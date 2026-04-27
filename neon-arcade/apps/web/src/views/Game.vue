<template>
  <div class="game-page">
    <!-- 返回按钮 -->
    <button class="back-btn" @click="goBack">
      ← 返回首页
    </button>

    <!-- 游戏组件 -->
    <component :is="gameComponent" v-if="gameComponent" />
    
    <div v-else class="empty-state">
      <p>😕 游戏不存在</p>
      <button class="back-btn-large" @click="goBack">返回首页</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGamesStore } from '../stores/games'

const route = useRoute()
const router = useRouter()
const gamesStore = useGamesStore()

const gameId = computed(() => route.params.id as string)

const currentGame = computed(() => {
  return gamesStore.games.find(g => g.id === gameId.value)
})

// 动态加载游戏组件
const gameComponent = computed(() => {
  if (!currentGame.value) return null
  
  const gameComponents: Record<string, any> = {
    'snake': defineAsyncComponent(() => import('../games/SnakeGame.vue')),
    'tetris': defineAsyncComponent(() => import('../games/TetrisGame.vue')),
    '2048': defineAsyncComponent(() => import('../games/Game2048.vue')),
    'airplane': defineAsyncComponent(() => import('../games/AirplaneGame.vue')),
    'whack-a-mole': defineAsyncComponent(() => import('../games/WhackAMoleGame.vue')),
    'sudoku': defineAsyncComponent(() => import('../games/SudokuGame.vue')),
    'match3': defineAsyncComponent(() => import('../games/Match3Home.vue'))
  }
  
  return gameComponents[currentGame.value.id] || null
})

function goBack() {
  router.push('/')
}
</script>

<style scoped>
.game-page {
  min-height: 100vh;
  background: #0a0a0a;
  position: relative;
}

.back-btn {
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 100;
  color: #fff;
  font-size: 1em;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #00f5ff;
  color: #00f5ff;
}

.empty-state {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 1.5em;
}

.back-btn-large {
  margin-top: 20px;
  padding: 12px 30px;
  background: transparent;
  border: 2px solid #00f5ff;
  color: #00f5ff;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s;
}

.back-btn-large:hover {
  background: #00f5ff;
  color: #0a0a0a;
}
</style>
