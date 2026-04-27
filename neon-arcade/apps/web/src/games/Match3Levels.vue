<template>
  <div class="match3-levels">
    <h1 class="game-title">NEON MATCH 3</h1>
    <p class="subtitle">霓虹消消乐 - 关卡模式</p>
    
    <!-- 总进度 -->
    <div class="total-progress">
      <div class="progress-info">
        <span class="progress-label">总进度</span>
        <span class="progress-value">{{ totalStars }} / {{ maxStars }} ⭐</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
    </div>
    
    <!-- 关卡列表 -->
    <div class="levels-grid">
      <div 
        v-for="level in LEVELS" 
        :key="level.id"
        class="level-card"
        :class="{ 
          'locked': !isUnlocked(level.id),
          'current': isCurrent(level.id)
        }"
        @click="selectLevel(level.id)"
      >
        <div class="level-number">{{ level.id }}</div>
        <div class="level-name">{{ level.name }}</div>
        <div class="level-stars">
          <span 
            v-for="i in 3" 
            :key="i" 
            class="star"
            :class="{ 'earned': i <= getLevelStars(level.id) }"
          >⭐</span>
        </div>
        <div v-if="!isUnlocked(level.id)" class="lock-icon">🔒</div>
      </div>
    </div>
    
    <!-- 返回按钮 -->
    <button class="back-btn" @click="goBack">← 返回游戏主页</button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { LEVELS, getLevelProgress, getTotalStars, TOTAL_LEVELS } from './match3Levels'

const router = useRouter()

// 关卡进度
const levelProgress = ref({ stars: [] as number[], unlocked: [] as boolean[] })

// 计算属性
const totalStars = computed(() => getTotalStars())
const maxStars = computed(() => TOTAL_LEVELS * 3)
const progressPercent = computed(() => (totalStars.value / maxStars.value) * 100)

// 获取关卡星星数
function getLevelStars(levelId: number): number {
  return levelProgress.value.stars[levelId - 1] || 0
}

// 检查关卡是否解锁
function isUnlocked(levelId: number): boolean {
  return levelProgress.value.unlocked[levelId - 1] || levelId === 1
}

// 检查是否是当前可玩的关卡
function isCurrent(levelId: number): boolean {
  return isUnlocked(levelId) && getLevelStars(levelId) === 0
}

// 选择关卡
function selectLevel(levelId: number) {
  if (!isUnlocked(levelId)) return
  router.push(`/game/match3-level/${levelId}`)
}

// 返回
function goBack() {
  router.push('/game/match3')
}

onMounted(() => {
  levelProgress.value = getLevelProgress()
})
</script>

<style scoped>
.match3-levels {
  min-height: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
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

.total-progress {
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 30px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.progress-label {
  color: #888;
}

.progress-value {
  color: #ffd700;
  font-weight: bold;
}

.progress-bar {
  height: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #ffd700, #ffed4a);
  border-radius: 5px;
  transition: width 0.3s ease;
}

.levels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 15px;
  width: 100%;
  max-width: 500px;
  margin-bottom: 30px;
}

.level-card {
  aspect-ratio: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.level-card:not(.locked):hover {
  transform: translateY(-5px);
  border-color: #ff00ff;
  box-shadow: 0 10px 30px rgba(255, 0, 255, 0.3);
}

.level-card.locked {
  opacity: 0.5;
  cursor: not-allowed;
}

.level-card.current {
  border-color: #00f5ff;
  box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
}

.level-number {
  font-size: 2em;
  font-weight: bold;
  color: #fff;
}

.level-name {
  font-size: 0.75em;
  color: #888;
  margin-top: 5px;
  text-align: center;
  padding: 0 5px;
}

.level-stars {
  margin-top: 8px;
  display: flex;
  gap: 2px;
}

.star {
  font-size: 0.9em;
  opacity: 0.3;
}

.star.earned {
  opacity: 1;
}

.lock-icon {
  position: absolute;
  font-size: 1.5em;
  opacity: 0.7;
}

.back-btn {
  padding: 12px 30px;
  background: transparent;
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1em;
  transition: all 0.3s;
}

.back-btn:hover {
  border-color: #00f5ff;
  color: #00f5ff;
}

@media (max-width: 768px) {
  .game-title {
    font-size: 1.8em;
  }
  
  .levels-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
