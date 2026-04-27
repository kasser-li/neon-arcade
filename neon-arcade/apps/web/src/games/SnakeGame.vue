<template>
  <div class="snake-game">
    <h1 class="game-title">NEON SNAKE</h1>
    
    <div class="game-info">
      <div class="info-item">
        <span>{{ score }}</span>
        得分
      </div>
      <div class="info-item">
        <span>{{ highScore }}</span>
        最高分
      </div>
    </div>
    
    <div class="game-container">
      <canvas
        ref="canvasRef"
        :width="canvasWidth"
        :height="canvasHeight"
        class="game-canvas"
      ></canvas>
      
      <div v-if="gameOver" class="game-over-overlay">
        <h2>GAME OVER</h2>
        <button class="restart-btn" @click="restartGame">重新开始</button>
      </div>
      
      <div v-if="!gameStarted" class="start-overlay">
        <button class="start-btn" @click="startGame">开始游戏</button>
      </div>
    </div>
    
    <p class="game-tip">🎮 操作说明：使用方向键 ↑ ↓ ← → 控制蛇移动</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref<HTMLCanvasElement | null>(null)
const canvasWidth = 600
const canvasHeight = 400
const gridSize = 20

const score = ref(0)
const highScore = ref(0)
const gameOver = ref(false)
const gameStarted = ref(false)

let ctx: CanvasRenderingContext2D | null = null
let snake: { x: number; y: number }[] = []
let food: { x: number; y: number } = { x: 0, y: 0 }
let direction: string = 'right'
let nextDirection: string = 'right'
let gameLoop: number | null = null

function initGame() {
  snake = [
    { x: 5, y: 10 },
    { x: 4, y: 10 },
    { x: 3, y: 10 }
  ]
  direction = 'right'
  nextDirection = 'right'
  score.value = 0
  gameOver.value = false
  generateFood()
}

function generateFood() {
  const maxX = canvasWidth / gridSize - 1
  const maxY = canvasHeight / gridSize - 1
  
  do {
    food.x = Math.floor(Math.random() * maxX)
    food.y = Math.floor(Math.random() * maxY)
  } while (snake.some(segment => segment.x === food.x && segment.y === food.y))
}

function draw() {
  if (!ctx) return
  
  // 清空画布
  ctx.fillStyle = '#0a0a0a'
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)
  
  // 绘制网格
  ctx.strokeStyle = 'rgba(0, 245, 255, 0.1)'
  ctx.lineWidth = 1
  for (let x = 0; x <= canvasWidth; x += gridSize) {
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, canvasHeight)
    ctx.stroke()
  }
  for (let y = 0; y <= canvasHeight; y += gridSize) {
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(canvasWidth, y)
    ctx.stroke()
  }
  
  // 绘制食物
  ctx.fillStyle = '#ff00ff'
  ctx.shadowColor = '#ff00ff'
  ctx.shadowBlur = 15
  ctx.fillRect(food.x * gridSize + 2, food.y * gridSize + 2, gridSize - 4, gridSize - 4)
  ctx.shadowBlur = 0
  
  // 绘制蛇
  snake.forEach((segment, index) => {
    const gradient = ctx!.createLinearGradient(
      segment.x * gridSize,
      segment.y * gridSize,
      (segment.x + 1) * gridSize,
      (segment.y + 1) * gridSize
    )
    gradient.addColorStop(0, '#00f5ff')
    gradient.addColorStop(1, '#0080ff')
    
    ctx!.fillStyle = gradient
    ctx!.shadowColor = '#00f5ff'
    ctx!.shadowBlur = index === 0 ? 20 : 10
    ctx!.fillRect(segment.x * gridSize + 1, segment.y * gridSize + 1, gridSize - 2, gridSize - 2)
    ctx!.shadowBlur = 0
  })
}

function update() {
  if (gameOver.value || !gameStarted.value) return
  
  direction = nextDirection
  
  const head = { ...snake[0] }
  
  switch (direction) {
    case 'up': head.y--
      break
    case 'down': head.y++
      break
    case 'left': head.x--
      break
    case 'right': head.x++
      break
  }
  
  // 检查撞墙
  const maxX = canvasWidth / gridSize - 1
  const maxY = canvasHeight / gridSize - 1
  if (head.x < 0 || head.x > maxX || head.y < 0 || head.y > maxY) {
    endGame()
    return
  }
  
  // 检查撞到自己
  if (snake.some(segment => segment.x === head.x && segment.y === head.y)) {
    endGame()
    return
  }
  
  snake.unshift(head)
  
  // 检查吃到食物
  if (head.x === food.x && head.y === food.y) {
    score.value += 10
    if (score.value > highScore.value) {
      highScore.value = score.value
    }
    generateFood()
  } else {
    snake.pop()
  }
  
  draw()
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
  draw()
  gameLoop = window.setInterval(update, 100)
}

function restartGame() {
  if (gameLoop) {
    clearInterval(gameLoop)
    gameLoop = null
  }
  gameStarted.value = true
  gameOver.value = false
  initGame()
  draw()
  gameLoop = window.setInterval(update, 100)
}

function handleKeydown(e: KeyboardEvent) {
  if (!gameStarted.value || gameOver.value) return
  
  switch (e.key) {
    case 'ArrowUp':
      if (direction !== 'down') nextDirection = 'up'
      break
    case 'ArrowDown':
      if (direction !== 'up') nextDirection = 'down'
      break
    case 'ArrowLeft':
      if (direction !== 'right') nextDirection = 'left'
      break
    case 'ArrowRight':
      if (direction !== 'left') nextDirection = 'right'
      break
  }
}

onMounted(() => {
  if (canvasRef.value) {
    ctx = canvasRef.value.getContext('2d')
    initGame()
    draw()
    
    // 添加触摸事件
    canvasRef.value.addEventListener('touchstart', handleTouchStart, { passive: false })
    canvasRef.value.addEventListener('touchmove', handleTouchMove, { passive: false })
    canvasRef.value.addEventListener('touchend', handleTouchEnd, { passive: false })
  }
  window.addEventListener('keydown', handleKeydown)
})

// 触摸控制
let touchStartX = 0
let touchStartY = 0

function handleTouchStart(e: TouchEvent) {
  touchStartX = e.touches[0].clientX
  touchStartY = e.touches[0].clientY
}

function handleTouchMove(e: TouchEvent) {
  if (!gameStarted.value || gameOver.value) return
  e.preventDefault()
}

function handleTouchEnd(e: TouchEvent) {
  if (!gameStarted.value || gameOver.value) return
  
  const touchEndX = e.changedTouches[0].clientX
  const touchEndY = e.changedTouches[0].clientY
  
  const dx = touchEndX - touchStartX
  const dy = touchEndY - touchStartY
  
  if (Math.abs(dx) > Math.abs(dy)) {
    // 水平滑动
    if (dx > 0 && direction !== 'left') nextDirection = 'right'
    else if (dx < 0 && direction !== 'right') nextDirection = 'left'
  } else {
    // 垂直滑动
    if (dy > 0 && direction !== 'up') nextDirection = 'down'
    else if (dy < 0 && direction !== 'down') nextDirection = 'up'
  }
}

onUnmounted(() => {
  if (gameLoop) {
    clearInterval(gameLoop)
  }
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.snake-game {
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
}

.game-over-overlay,
.start-overlay {
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

.game-over-overlay h2 {
  color: #ff00ff;
  font-size: 2em;
  margin-bottom: 20px;
  text-shadow: 0 0 20px #ff00ff;
}

.restart-btn,
.start-btn {
  padding: 12px 30px;
  font-size: 1.1em;
  background: transparent;
  border: 2px solid #00f5ff;
  color: #00f5ff;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s;
}

.restart-btn:hover,
.start-btn:hover {
  background: #00f5ff;
  color: #0a0a0a;
  box-shadow: 0 0 30px #00f5ff;
}

.game-tip {
  margin-top: 15px;
  color: #888;
  font-size: 0.9em;
}
</style>
