<template>
  <div class="whack-game">
    <h1 class="game-title">WHACK-A-MOLE</h1>
    
    <div class="game-info">
      <div class="info-item">
        <span>{{ score }}</span>
        得分
      </div>
      <div class="info-item">
        <span>{{ timeLeft }}</span>
        时间
      </div>
      <div class="info-item">
        <span>{{ combo }}</span>
        连击
      </div>
    </div>
    
    <div class="difficulty-selector" v-if="!gameStarted">
      <button 
        v-for="diff in difficulties" 
        :key="diff.level"
        :class="['diff-btn', { active: selectedDiff === diff.level }]"
        @click="selectedDiff = diff.level"
      >
        {{ diff.label }}
      </button>
    </div>
    
    <div class="game-board">
      <div 
        v-for="(hole, index) in holes" 
        :key="index"
        class="hole"
        :class="{ active: hole.active, hit: hole.hit }"
        @mousedown="whack(index)"
        @touchstart.prevent="whack(index)"
      >
        <div class="mole" v-if="hole.active">
          <span class="mole-face">🐹</span>
        </div>
        <div class="hit-effect" v-if="hole.hit">💥</div>
      </div>
    </div>
    
    <div v-if="!gameStarted && !gameOver" class="start-screen">
      <button class="start-btn" @click="startGame">开始游戏</button>
    </div>
    
    <div v-if="gameOver" class="overlay">
      <h2>游戏结束</h2>
      <p>最终得分: {{ score }}</p>
      <p>最高连击: {{ maxCombo }}</p>
      <button @click="restartGame">再玩一次</button>
    </div>
    
    <p class="game-tip">🎮 点击地鼠得分，连击有加成！</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const GRID_SIZE = 3
const GAME_DURATION = 60

const difficulties = [
  { level: 'easy', label: '简单', spawnInterval: 1000, stayTime: 1500 },
  { level: 'medium', label: '中等', spawnInterval: 800, stayTime: 1200 },
  { level: 'hard', label: '困难', spawnInterval: 600, stayTime: 900 }
]

const selectedDiff = ref('medium')
const score = ref(0)
const timeLeft = ref(GAME_DURATION)
const combo = ref(0)
const maxCombo = ref(0)
const gameOver = ref(false)
const gameStarted = ref(false)

const holes = ref(Array(9).fill(null).map(() => ({ active: false, hit: false, timeout: 0 })))

let gameLoop: number | null = null
let timerLoop: number | null = null
let spawnLoop: number | null = null

function getDifficulty() {
  return difficulties.find(d => d.level === selectedDiff.value) || difficulties[1]
}

function initGame() {
  score.value = 0
  timeLeft.value = GAME_DURATION
  combo.value = 0
  maxCombo.value = 0
  gameOver.value = false
  holes.value = Array(9).fill(null).map(() => ({ active: false, hit: false, timeout: 0 }))
}

function spawnMole() {
  const emptyHoles = holes.value
    .map((h, i) => ({ hole: h, index: i }))
    .filter(h => !h.hole.active && !h.hole.hit)
  
  if (emptyHoles.length === 0) return
  
  const { index } = emptyHoles[Math.floor(Math.random() * emptyHoles.length)]
  const diff = getDifficulty()
  
  holes.value[index].active = true
  holes.value[index].hit = false
  
  // 地鼠停留时间
  setTimeout(() => {
    if (holes.value[index].active) {
      holes.value[index].active = false
      combo.value = 0 // 没打到，连击中断
    }
  }, diff.stayTime)
}

function whack(index: number) {
  if (!gameStarted.value || gameOver.value) return
  
  const hole = holes.value[index]
  
  if (hole.active && !hole.hit) {
    hole.hit = true
    hole.active = false
    combo.value++
    if (combo.value > maxCombo.value) {
      maxCombo.value = combo.value
    }
    
    // 连击加成
    const bonus = Math.floor(combo.value / 5) * 5
    score.value += 10 + bonus
    
    // 显示击中效果
    setTimeout(() => {
      hole.hit = false
    }, 200)
  }
}

function startGame() {
  gameStarted.value = true
  initGame()
  
  const diff = getDifficulty()
  
  // 游戏计时
  timerLoop = window.setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) {
      endGame()
    }
  }, 1000)
  
  // 生成地鼠
  spawnLoop = window.setInterval(() => {
    spawnMole()
  }, diff.spawnInterval)
}

function endGame() {
  gameOver.value = true
  gameStarted.value = false
  
  if (timerLoop) {
    clearInterval(timerLoop)
    timerLoop = null
  }
  if (spawnLoop) {
    clearInterval(spawnLoop)
    spawnLoop = null
  }
}

function restartGame() {
  gameOver.value = false
  startGame()
}

onUnmounted(() => {
  if (timerLoop) clearInterval(timerLoop)
  if (spawnLoop) clearInterval(spawnLoop)
})
</script>

<style scoped>
.whack-game {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: #0a0a0a;
  min-height: 100%;
}

.game-title {
  color: #8B4513;
  text-shadow: 0 0 20px #D2691E, 0 0 40px #8B4513;
  font-size: 2em;
  margin-bottom: 15px;
  letter-spacing: 5px;
}

.game-info {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.info-item {
  text-align: center;
  padding: 8px 15px;
  background: rgba(139, 69, 19, 0.2);
  border: 1px solid #8B4513;
  border-radius: 10px;
  box-shadow: 0 0 15px rgba(139, 69, 19, 0.3);
  color: #fff;
  font-size: 0.9em;
}

.info-item span {
  display: block;
  font-size: 1.5em;
  font-weight: bold;
  color: #D2691E;
}

.difficulty-selector {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.diff-btn {
  padding: 8px 20px;
  background: transparent;
  border: 2px solid #8B4513;
  color: #8B4513;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.diff-btn.active,
.diff-btn:hover {
  background: #8B4513;
  color: #fff;
}

.game-board {
  display: grid;
  grid-template-columns: repeat(3, 100px);
  grid-template-rows: repeat(3, 100px);
  gap: 15px;
  padding: 20px;
  background: linear-gradient(45deg, #8B4513, #D2691E, #8B4513);
  border-radius: 15px;
}

.hole {
  width: 100px;
  height: 100px;
  background: #3d1f0a;
  border-radius: 50%;
  position: relative;
  cursor: pointer;
  box-shadow: inset 0 10px 20px rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.hole.active {
  background: #5a2d12;
}

.mole {
  animation: popUp 0.2s ease-out;
}

.mole-face {
  font-size: 3em;
  filter: drop-shadow(0 0 10px #D2691E);
}

.hit-effect {
  position: absolute;
  font-size: 2.5em;
  animation: hitAnim 0.2s ease-out;
}

@keyframes popUp {
  0% { transform: translateY(50px); opacity: 0; }
  100% { transform: translateY(0); opacity: 1; }
}

@keyframes hitAnim {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

.start-screen,
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.9);
  z-index: 100;
}

.overlay h2 {
  color: #D2691E;
  font-size: 2em;
  margin-bottom: 15px;
}

.overlay p {
  color: #fff;
  font-size: 1.2em;
  margin: 5px 0;
}

.start-btn,
.overlay button {
  padding: 15px 40px;
  font-size: 1.2em;
  background: transparent;
  border: 3px solid #D2691E;
  color: #D2691E;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 20px;
}

.start-btn:hover,
.overlay button:hover {
  background: #D2691E;
  color: #fff;
  box-shadow: 0 0 30px #D2691E;
}

.game-tip {
  margin-top: 15px;
  color: #888;
  font-size: 0.9em;
}

@media (max-width: 768px) {
  .game-board {
    grid-template-columns: repeat(3, 80px);
    grid-template-rows: repeat(3, 80px);
    gap: 10px;
    padding: 15px;
  }
  
  .hole {
    width: 80px;
    height: 80px;
  }
  
  .mole-face {
    font-size: 2.5em;
  }
}
</style>
