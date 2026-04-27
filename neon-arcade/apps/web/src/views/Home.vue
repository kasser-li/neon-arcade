<template>
  <div class="home">
    <!-- 背景星星 -->
    <div class="stars">
      <div v-for="i in 100" :key="i" class="star" :style="getStarStyle(i)"></div>
    </div>

    <!-- 头部 -->
    <header class="header">
      <h1 class="title">NEON ARCADE</h1>
      <p class="subtitle">霓虹游戏站 · 经典小游戏合集</p>
      <div class="header-actions">
        <button class="header-btn" @click="goToNovel">📖 小说</button>
        <button class="header-btn" @click="goToProfile">👤 个人中心</button>
        <button class="header-btn" @click="goToLeaderboard">🏆 排行榜</button>
      </div>
    </header>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <input
        v-model="searchInput"
        type="text"
        placeholder="搜索游戏..."
        class="search-input"
        @input="handleSearch"
      >
    </div>

    <!-- 分类标签 -->
    <div class="categories">
      <button
        v-for="cat in categories"
        :key="cat.id"
        :class="['category-btn', { active: activeCategory === cat.id }]"
        @click="setCategory(cat.id)"
      >
        {{ cat.label }}
      </button>
    </div>

    <!-- 游戏列表 -->
    <div class="games-grid">
      <div
        v-for="game in gamesStore.filteredGames"
        :key="game.id"
        class="game-card"
        :style="{ '--color1': game.color[0], '--color2': game.color[1] }"
        @click="goToGame(game)"
      >
        <span class="game-tag">{{ game.categoryLabel }}</span>
        <span class="game-icon">{{ game.icon }}</span>
        <h2 class="game-name">{{ game.name }}</h2>
        <p class="game-desc">{{ game.description }}</p>
        <button class="play-btn">开始游戏</button>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="gamesStore.filteredGames.length === 0" class="empty-state">
      <p>😕 没有找到匹配的游戏</p>
      <p class="empty-hint">试试其他关键词或分类</p>
    </div>

    <!-- 底部 -->
    <footer class="footer">
      <p>使用方向键或触摸控制 · 支持手机/电脑</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useGamesStore } from '../stores/games'

const router = useRouter()
const gamesStore = useGamesStore()

const { categories, setCategory } = gamesStore
const activeCategory = computed(() => gamesStore.activeCategory)

const searchInput = ref('')

function handleSearch() {
  gamesStore.setSearch(searchInput.value)
}

function goToGame(game: any) {
  router.push(`/game/${game.id}`)
}

function getStarStyle(i: number) {
  return {
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    animationDelay: `${Math.random() * 2}s`
  }
}

function goToProfile() {
  router.push('/profile')
}

function goToLeaderboard() {
  router.push('/leaderboard')
}

function goToNovel() {
  router.push('/novel')
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  background: #0a0a0a;
}

/* 星星背景 */
.stars {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.star {
  position: absolute;
  width: 2px;
  height: 2px;
  background: #fff;
  border-radius: 50%;
  animation: twinkle 2s infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* 头部 */
.header {
  text-align: center;
  padding: 60px 20px 40px;
  position: relative;
  z-index: 1;
}

.title {
  font-size: 4em;
  letter-spacing: 15px;
  text-transform: uppercase;
  background: linear-gradient(90deg, #00f5ff, #ff00ff, #ffcc00, #00ff88, #00f5ff);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shine 3s linear infinite;
  text-shadow: 0 0 60px rgba(0, 245, 255, 0.5);
}

@keyframes shine {
  0% { background-position: 0% center; }
  100% { background-position: 200% center; }
}

.subtitle {
  color: #888;
  font-size: 1.2em;
  margin-top: 15px;
  letter-spacing: 5px;
}

/* 搜索栏 */
.search-bar {
  max-width: 500px;
  margin: 0 auto 30px;
  padding: 0 20px;
  position: relative;
  z-index: 1;
}

.search-input {
  width: 100%;
  padding: 15px 25px;
  font-size: 1em;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 50px;
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  outline: none;
  transition: all 0.3s;
}

.search-input:focus {
  border-color: #00f5ff;
  box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
}

.search-input::placeholder {
  color: #666;
}

/* 分类 */
.categories {
  display: flex;
  justify-content: center;
  gap: 15px;
  padding: 0 20px 30px;
  flex-wrap: wrap;
  position: relative;
  z-index: 1;
}

.category-btn {
  padding: 10px 25px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  background: transparent;
  color: #888;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.95em;
}

.category-btn:hover,
.category-btn.active {
  border-color: #00f5ff;
  color: #00f5ff;
  background: rgba(0, 245, 255, 0.1);
  box-shadow: 0 0 15px rgba(0, 245, 255, 0.3);
}

/* 游戏网格 */
.games-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 40px;
  position: relative;
  z-index: 1;
}

.game-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.game-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 20px;
  padding: 2px;
  background: linear-gradient(45deg, var(--color1), var(--color2));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.game-card:hover::before {
  opacity: 1;
}

.game-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
}

.game-tag {
  position: absolute;
  top: 15px;
  right: 15px;
  padding: 5px 12px;
  border-radius: 15px;
  font-size: 0.75em;
  color: #fff;
  background: var(--color1);
  opacity: 0.8;
}

.game-icon {
  font-size: 3.5em;
  margin-bottom: 15px;
  display: block;
}

.game-name {
  color: #fff;
  font-size: 1.6em;
  margin-bottom: 8px;
  letter-spacing: 3px;
}

.game-desc {
  color: #888;
  font-size: 0.9em;
  line-height: 1.5;
  margin-bottom: 20px;
}

.play-btn {
  display: inline-block;
  padding: 10px 30px;
  border: 2px solid var(--color1);
  background: transparent;
  color: var(--color1);
  border-radius: 30px;
  font-weight: bold;
  transition: all 0.3s;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-size: 0.9em;
  cursor: pointer;
}

.play-btn:hover {
  background: var(--color1);
  color: #0a0a0a;
  box-shadow: 0 0 30px var(--color1);
}

/* 空状态 */
.empty-state {
  text-align: center;
  color: #666;
  padding: 60px 20px;
}

.empty-hint {
  color: #444;
  margin-top: 10px;
}

/* 头部按钮 */
.header-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 20px;
}

.header-btn {
  padding: 10px 25px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 25px;
  color: #fff;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.95em;
}

.header-btn:hover {
  background: rgba(0, 245, 255, 0.1);
  border-color: #00f5ff;
  transform: translateY(-2px);
}

/* 底部 */
.footer {
  text-align: center;
  padding: 40px;
  color: #666;
  position: relative;
  z-index: 1;
}

@media (max-width: 768px) {
  .title {
    font-size: 2.5em;
    letter-spacing: 8px;
  }
  
  .games-grid {
    grid-template-columns: 1fr;
  }
  
  .header-actions {
    flex-wrap: wrap;
  }
}
</style>
