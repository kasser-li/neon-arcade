<template>
  <div class="admin-page">
    <header class="admin-header">
      <h1>🎮 游戏管理后台</h1>
      <button class="back-btn" @click="goHome">返回首页</button>
    </header>

    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-label">游戏总数</div>
        <div class="stat-value">{{ games.length }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">分类数量</div>
        <div class="stat-value">{{ categories.length - 1 }}</div>
      </div>
    </div>

    <div class="games-list">
      <div class="list-header">
        <span>游戏列表</span>
        <button class="add-btn" @click="showAddDialog">添加游戏</button>
      </div>
      
      <div class="game-item" v-for="game in games" :key="game.id">
        <span class="game-icon">{{ game.icon }}</span>
        <span class="game-name">{{ game.name }}</span>
        <span class="game-category">{{ game.categoryLabel }}</span>
        <button class="edit-btn" @click="editGame(game)">编辑</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useGamesStore } from '../stores/games'

const router = useRouter()
const gamesStore = useGamesStore()

const { games, categories } = gamesStore

function goHome() {
  router.push('/')
}

function showAddDialog() {
  alert('添加游戏功能开发中...')
}

function editGame(game: any) {
  alert(`编辑游戏: ${game.name}`)
}
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  padding: 20px;
  background: #0a0a0a;
  color: #fff;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 30px;
}

.back-btn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
}

.stat-value {
  font-size: 2em;
  color: #00f5ff;
}

.games-list {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.game-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.game-icon {
  font-size: 1.5em;
}

.game-name {
  flex: 1;
}

.add-btn, .edit-btn {
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  border: none;
}

.add-btn {
  background: #00f5ff;
  color: #000;
}

.edit-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}
</style>
