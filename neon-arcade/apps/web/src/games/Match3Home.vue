<template>
  <div class="match3-home">
    <button class="back-btn" @click="goBack">← 返回首页</button>
    <h1 class="game-title">NEON MATCH 3</h1>
    <p class="subtitle">霓虹消消乐</p>
    
    <div class="menu-container">
      <div class="menu-card">
        <div class="icon">∞</div>
        <h2>无尽模式</h2>
        <p>挑战最高分，没有时间限制</p>
        <button class="play-btn" @click="startEndless">开始游戏</button>
      </div>
      
      <div class="menu-card" @click="startLevels">
        <div class="icon">📋</div>
        <h2>关卡模式</h2>
        <p>挑战各种有趣关卡，解锁新关卡</p>
        <button class="play-btn">开始挑战</button>
      </div>
    </div>
    
    <div class="action-buttons">
      <button class="action-btn shop-btn" @click="goToShop">
        🛒 道具商店
      </button>
    </div>

    <div class="stats-panel">
      <div class="stat-item">
        <span class="stat-value">{{ highScore }}</span>
        <span class="stat-label">最高分</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ totalGames }}</span>
        <span class="stat-label">游戏次数</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ coins }}</span>
        <span class="stat-label">金币</span>
      </div>
    </div>
    
    <div class="how-to-play">
      <h3>🎮 游戏说明</h3>
      <ul>
        <li>交换相邻元素，3个或以上相同即可消除</li>
        <li>4连消生成火箭，5连消生成炸弹</li>
        <li>连击越多，分数加成越高</li>
        <li>无法移动时游戏结束</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMatch3ShopStore } from '../stores/match3Shop'

const router = useRouter()
const shopStore = useMatch3ShopStore()

const highScore = ref(0)
const totalGames = ref(0)
const coins = ref(0)

onMounted(() => {
  // 从本地存储读取数据
  highScore.value = parseInt(localStorage.getItem('match3_highscore') || '0')
  totalGames.value = parseInt(localStorage.getItem('match3_games') || '0')
  shopStore.loadData()
  coins.value = shopStore.coins
})

function startEndless() {
  router.push('/game/match3-endless')
}

function startLevels() {
  router.push('/game/match3-levels')
}

function goToShop() {
  router.push('/game/match3-shop')
}

function goBack() {
  router.push('/')
}
</script>

<style scoped>
.match3-home {
  min-height: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.back-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  color: #fff;
  font-size: 1em;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
  z-index: 10;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #00f5ff;
  color: #00f5ff;
}

.game-title {
  font-size: 2.5em;
  background: linear-gradient(45deg, #ff0066, #ff00ff, #00f5ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 30px rgba(255, 0, 255, 0.5);
  margin-bottom: 5px;
  letter-spacing: 5px;
}

.subtitle {
  color: #888;
  font-size: 1.1em;
  margin-bottom: 30px;
}

.menu-container {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
  justify-content: center;
}

.menu-card {
  width: 200px;
  padding: 25px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  text-align: center;
  transition: all 0.3s;
}

.menu-card:not(.disabled):hover {
  transform: translateY(-5px);
  border-color: #ff00ff;
  box-shadow: 0 10px 30px rgba(255, 0, 255, 0.3);
}

.menu-card.disabled {
  opacity: 0.5;
}

.menu-card .icon {
  font-size: 3em;
  margin-bottom: 10px;
}

.menu-card h2 {
  color: #fff;
  font-size: 1.3em;
  margin-bottom: 10px;
}

.menu-card p {
  color: #888;
  font-size: 0.9em;
  margin-bottom: 15px;
}

.play-btn {
  padding: 10px 30px;
  background: linear-gradient(45deg, #ff0066, #ff00ff);
  border: none;
  color: #fff;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1em;
  transition: all 0.3s;
}

.play-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(255, 0, 255, 0.5);
}

.play-btn:disabled {
  background: #444;
  cursor: not-allowed;
}

.action-buttons {
  margin-bottom: 20px;
}

.action-btn {
  padding: 12px 30px;
  background: linear-gradient(45deg, #ffd700, #ffed4a);
  border: none;
  border-radius: 25px;
  color: #0a0a0a;
  font-weight: bold;
  font-size: 1em;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
}

.stats-panel {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
  justify-content: center;
}

.stat-item {
  text-align: center;
  padding: 15px 25px;
  background: rgba(0, 245, 255, 0.1);
  border: 1px solid rgba(0, 245, 255, 0.3);
  border-radius: 10px;
}

.stat-value {
  display: block;
  font-size: 1.8em;
  font-weight: bold;
  color: #00f5ff;
}

.stat-label {
  display: block;
  color: #888;
  font-size: 0.9em;
  margin-top: 5px;
}

.how-to-play {
  max-width: 400px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
}

.how-to-play h3 {
  color: #fff;
  margin-bottom: 15px;
  text-align: center;
}

.how-to-play ul {
  list-style: none;
  padding: 0;
}

.how-to-play li {
  color: #aaa;
  padding: 8px 0;
  padding-left: 20px;
  position: relative;
}

.how-to-play li::before {
  content: "▸";
  position: absolute;
  left: 0;
  color: #ff00ff;
}

@media (max-width: 768px) {
  .game-title {
    font-size: 1.8em;
  }
  
  .menu-card {
    width: 150px;
    padding: 20px;
  }
}
</style>
