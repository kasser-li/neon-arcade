<template>
  <div class="airplane-game">
    <h1 class="game-title">AIRPLANE WAR</h1>
    
    <div class="game-info">
      <div class="info-item">
        <span>{{ score }}</span>
        得分
      </div>
      <div class="info-item">
        <span>{{ lives }}</span>
        生命
      </div>
    </div>
    
    <div class="game-container">
      <canvas
        ref="canvasRef"
        :width="canvasWidth"
        :height="canvasHeight"
        class="game-canvas"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
      ></canvas>
      
      <div v-if="gameOver" class="overlay">
        <h2>GAME OVER</h2>
        <button @click="restartGame">重新开始</button>
      </div>
      
      <div v-if="!gameStarted" class="overlay">
        <button @click="startGame">开始游戏</button>
      </div>
    </div>
    
    <div class="touch-controls" v-if="gameStarted && !gameOver">
      <button class="fire-btn" @touchstart.prevent="startFiring" @touchend.prevent="stopFiring" @mousedown.prevent="startFiring" @mouseup.prevent="stopFiring">🔥 发射</button>
    </div>
    
    <p class="game-tip">🎮 操作：拖动飞机移动，点击发射子弹</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const canvasWidth = 400
const canvasHeight = 600

const canvasRef = ref<HTMLCanvasElement | null>(null)
const score = ref(0)
const lives = ref(3)
const gameOver = ref(false)
const gameStarted = ref(false)

let ctx: CanvasRenderingContext2D | null = null
let gameLoop: number | null = null
let isFiring = false

// 游戏对象
let player = { x: 200, y: 550, width: 40, height: 40 }
let bullets: { x: number; y: number; speed: number }[] = []
let enemies: { x: number; y: number; width: number; height: number; speed: number; hp: number }[] = []
let particles: { x: number; y: number; vx: number; vy: number; life: number; color: string }[] = []

function initGame() {
  player = { x: 200, y: 550, width: 40, height: 40 }
  bullets = []
  enemies = []
  particles = []
  score.value = 0
  lives.value = 3
  gameOver.value = false
  isFiring = false
}

function spawnEnemy() {
  if (Math.random() < 0.02) {
    enemies.push({
      x: Math.random() * (canvasWidth - 40),
      y: -40,
      width: 40,
      height: 40,
      speed: 2 + Math.random() * 2,
      hp: 1
    })
  }
}

function createExplosion(x: number, y: number, color: string) {
  for (let i = 0; i < 10; i++) {
    particles.push({
      x,
      y,
      vx: (Math.random() - 0.5) * 8,
      vy: (Math.random() - 0.5) * 8,
      life: 30,
      color
    })
  }
}

function draw() {
  if (!ctx) return
  
  // 清空画布
  ctx.fillStyle = '#0a0a0a'
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)
  
  // 绘制星空背景
  ctx.fillStyle = '#fff'
  for (let i = 0; i < 50; i++) {
    const x = (i * 37) % canvasWidth
    const y = (i * 23 + Date.now() / 50) % canvasHeight
    ctx.fillRect(x, y, 1, 1)
  }
  
  // 绘制玩家飞机
  ctx.fillStyle = '#00f5ff'
  ctx.shadowColor = '#00f5ff'
  ctx.shadowBlur = 20
  ctx.beginPath()
  ctx.moveTo(player.x + player.width / 2, player.y)
  ctx.lineTo(player.x, player.y + player.height)
  ctx.lineTo(player.x + player.width / 2, player.y + player.height - 10)
  ctx.lineTo(player.x + player.width, player.y + player.height)
  ctx.closePath()
  ctx.fill()
  ctx.shadowBlur = 0
  
  // 绘制子弹
  ctx.fillStyle = '#ff0'
  bullets.forEach(bullet => {
    ctx.fillRect(bullet.x - 2, bullet.y, 4, 10)
  })
  
  // 绘制敌人
  enemies.forEach(enemy => {
    ctx.fillStyle = '#ff00ff'
    ctx.shadowColor = '#ff00ff'
    ctx.shadowBlur = 15
    ctx.fillRect(enemy.x, enemy.y, enemy.width, enemy.height)
    ctx.shadowBlur = 0
  })
  
  // 绘制粒子
  particles.forEach(p => {
    ctx.fillStyle = p.color
    ctx.globalAlpha = p.life / 30
    ctx.fillRect(p.x, p.y, 3, 3)
    ctx.globalAlpha = 1
  })
}

function update() {
  if (gameOver.value || !gameStarted.value) return
  
  // 发射子弹
  if (isFiring && Math.random() < 0.3) {
    bullets.push({ x: player.x + player.width / 2, y: player.y, speed: 8 })
  }
  
  // 更新子弹
  bullets = bullets.filter(bullet => {
    bullet.y -= bullet.speed
    return bullet.y > -10
  })
  
  // 生成敌人
  spawnEnemy()
  
  // 更新敌人
  enemies = enemies.filter(enemy => {
    enemy.y += enemy.speed
    
    // 碰撞检测 - 子弹打敌人
    bullets.forEach((bullet, bi) => {
      if (bullet.x > enemy.x && bullet.x < enemy.x + enemy.width &&
          bullet.y > enemy.y && bullet.y < enemy.y + enemy.height) {
        enemy.hp--
        bullets.splice(bi, 1)
        if (enemy.hp <= 0) {
          score.value += 10
          createExplosion(enemy.x + enemy.width / 2, enemy.y + enemy.height / 2, '#ff00ff')
        }
      }
    })
    
    // 碰撞检测 - 敌人撞玩家
    if (enemy.x < player.x + player.width && enemy.x + enemy.width > player.x &&
        enemy.y < player.y + player.height && enemy.y + enemy.height > player.y) {
      lives.value--
      createExplosion(player.x + player.width / 2, player.y + player.height / 2, '#00f5ff')
      if (lives.value <= 0) {
        endGame()
      }
      return false
    }
    
    return enemy.y < canvasHeight + 40 && enemy.hp > 0
  })
  
  // 更新粒子
  particles = particles.filter(p => {
    p.x += p.vx
    p.y += p.vy
    p.life--
    return p.life > 0
  })
}

function endGame() {
  gameOver.value = true
  if (gameLoop) {
    clearInterval(gameLoop)
    gameLoop = null
  }
}

function startGame() {
  gameStarted.value = true
  initGame()
  gameLoop = window.setInterval(() => {
    update()
    draw()
  }, 1000 / 60)
}

function restartGame() {
  if (gameLoop) {
    clearInterval(gameLoop)
    gameLoop = null
  }
  gameStarted.value = true
  gameOver.value = false
  initGame()
  gameLoop = window.setInterval(() => {
    update()
    draw()
  }, 1000 / 60)
}

// 触摸控制
let touchId: number | null = null

function handleTouchStart(e: TouchEvent) {
  if (!gameStarted.value || gameOver.value) return
  const touch = e.touches[0]
  const rect = canvasRef.value?.getBoundingClientRect()
  if (rect) {
    player.x = touch.clientX - rect.left - player.width / 2
    player.x = Math.max(0, Math.min(canvasWidth - player.width, player.x))
  }
}

function handleTouchMove(e: TouchEvent) {
  if (!gameStarted.value || gameOver.value) return
  e.preventDefault()
  const touch = e.touches[0]
  const rect = canvasRef.value?.getBoundingClientRect()
  if (rect) {
    player.x = touch.clientX - rect.left - player.width / 2
    player.x = Math.max(0, Math.min(canvasWidth - player.width, player.x))
  }
}

function handleTouchEnd(e: TouchEvent) {
  // 触摸结束
}

function startFiring() {
  isFiring = true
}

function stopFiring() {
  isFiring = false
}

onMounted(() => {
  if (canvasRef.value) {
    ctx = canvasRef.value.getContext('2d')
    initGame()
    draw()
  }
})

onUnmounted(() => {
  if (gameLoop) {
    clearInterval(gameLoop)
  }
})
</script>

<style scoped>
.airplane-game {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: #0a0a0a;
  min-height: 100%;
}

.game-title {
  color: #00f5ff;
  text-shadow: 0 0 20px #00f5ff, 0 0 40px #00f5ff;
  font-size: 2em;
  margin-bottom: 15px;
  letter-spacing: 5px;
}

.game-info {
  display: flex;
  gap: 30px;
  margin-bottom: 15px;
}

.info-item {
  text-align: center;
  padding: 8px 20px;
  background: rgba(0, 245, 255, 0.1);
  border: 1px solid #00f5ff;
  border-radius: 10px;
  box-shadow: 0 0 15px rgba(0, 245, 255, 0.3);
  color: #fff;
  font-size: 0.9em;
}

.info-item span {
  display: block;
  font-size: 1.5em;
  font-weight: bold;
  color: #00f5ff;
}

.game-container {
  position: relative;
  padding: 3px;
  background: linear-gradient(45deg, #00f5ff, #ff00ff, #00f5ff);
  border-radius: 10px;
}

.game-canvas {
  display: block;
  background: #0a0a0a;
  border-radius: 8px;
  touch-action: none;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.8);
  border-radius: 8px;
}

.overlay h2 {
  color: #ff00ff;
  font-size: 2em;
  margin-bottom: 20px;
  text-shadow: 0 0 20px #ff00ff;
}

.overlay button {
  padding: 12px 30px;
  font-size: 1.1em;
  background: transparent;
  border: 2px solid #00f5ff;
  color: #00f5ff;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s;
}

.overlay button:hover {
  background: #00f5ff;
  color: #0a0a0a;
}

.touch-controls {
  margin-top: 15px;
}

.fire-btn {
  padding: 20px 50px;
  font-size: 1.2em;
  background: rgba(255, 0, 0, 0.3);
  border: 3px solid #ff0000;
  color: #ff0000;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.1s;
  user-select: none;
}

.fire-btn:active {
  background: #ff0000;
  color: #fff;
  transform: scale(0.95);
}

.game-tip {
  margin-top: 15px;
  color: #888;
  font-size: 0.9em;
}

@media (max-width: 768px) {
  .game-canvas {
    width: 100%;
    max-width: 400px;
  }
}
</style>
