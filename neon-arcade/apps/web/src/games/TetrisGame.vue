<template>
  <div class="tetris-game">
    <h1 class="game-title">NEON TETRIS</h1>
    
    <div class="game-layout">
      <!-- 左侧信息面板 -->
      <div class="side-panel left">
        <div class="preview-box">
          <span class="box-label">下一个</span>
          <div class="next-piece" v-if="nextPieceShape">
            <div 
              v-for="(row, y) in nextPieceShape" 
              :key="y"
              class="next-row"
            >
              <div
                v-for="(cell, x) in row"
                :key="x"
                class="next-cell"
                :class="{ filled: cell !== 0, [`color-${cell}`]: cell !== 0 }"
              ></div>
            </div>
          </div>
        </div>
        
        <div class="info-box">
          <span class="info-label">得分</span>
          <span class="info-value">{{ score }}</span>
        </div>
        
        <div class="info-box">
          <span class="info-label">消除</span>
          <span class="info-value">{{ lines }}</span>
        </div>
        
        <div class="info-box">
          <span class="info-label">等级</span>
          <span class="info-value">{{ level }}</span>
        </div>
        
        <button class="pause-btn" @click="togglePause" v-if="gameStarted && !gameOver">
          {{ isPaused ? '▶' : '⏸' }}
        </button>
      </div>
      
      <!-- 中间游戏区域 -->
      <div class="game-area">
        <div class="board" :class="{ paused: isPaused }">
          <!-- 已固定的方块 -->
          <div 
            v-for="(cell, index) in board" 
            :key="`board-${index}`"
            class="cell"
            :class="{ filled: cell !== 0, [`color-${cell}`]: cell !== 0 }"
          ></div>
          
          <!-- 幽灵方块（落点预览） -->
          <div 
            v-for="(pos, index) in ghostPositions" 
            :key="`ghost-${index}`"
            class="ghost-cell"
            :class="[`color-${currentPiece?.color}`]"
            :style="{ 
              gridRow: pos.y + 1, 
              gridColumn: pos.x + 1 
            }"
          ></div>
          
          <!-- 当前下落的方块 -->
          <div 
            v-for="(pos, index) in currentPiecePositions" 
            :key="`piece-${index}`"
            class="piece-cell"
            :class="[`color-${currentPiece?.color}`]"
            :style="{ 
              gridRow: pos.y + 1, 
              gridColumn: pos.x + 1 
            }"
          ></div>
        </div>
        
        <!-- 游戏结束/开始遮罩 -->
        <div v-if="!gameStarted || gameOver" class="overlay">
          <h2>{{ gameOver ? 'GAME OVER' : 'READY?' }}</h2>
          <p v-if="gameOver" class="final-score">得分: {{ score }}</p>
          <button @click="gameOver ? restartGame() : startGame()">
            {{ gameOver ? '再来一局' : '开始游戏' }}
          </button>
        </div>
        
        <!-- 暂停遮罩 -->
        <div v-if="isPaused" class="overlay pause-overlay">
          <h2>PAUSED</h2>
          <button @click="togglePause">继续</button>
        </div>
      </div>
    </div>
    
    <!-- 桌面端操作提示 -->
    <p class="game-tip desktop-only">
      ← → 移动 | ↑ 旋转 | ↓ 加速 | 空格 落下 | P 暂停
    </p>
    
    <!-- 移动端触摸控制 -->
    <div class="mobile-controls" v-if="gameStarted && !gameOver && !isPaused">
      <div class="control-group left">
        <button class="control-btn rotate" @click="rotate">↻</button>
        <button class="control-btn drop" @click="softDrop">↓</button>
        <button class="control-btn hard-drop" @click="hardDrop">⬇</button>
      </div>
      <div class="control-group right">
        <button class="control-btn left" @click="moveLeft">←</button>
        <button class="control-btn right" @click="moveRight">→</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 游戏配置
const BOARD_WIDTH = 10
const BOARD_HEIGHT = 20
const DROP_INTERVAL_BASE = 1000

// 方块形状
const SHAPES = [
  { shape: [[1, 1, 1, 1]], color: 1 },                    // I
  { shape: [[2, 2], [2, 2]], color: 2 },                  // O
  { shape: [[0, 3, 0], [3, 3, 3]], color: 3 },            // T
  { shape: [[0, 4, 4], [4, 4, 0]], color: 4 },            // S
  { shape: [[5, 5, 0], [0, 5, 5]], color: 5 },            // Z
  { shape: [[6, 0, 0], [6, 6, 6]], color: 6 },            // J
  { shape: [[0, 0, 7], [7, 7, 7]], color: 7 }             // L
]

// 游戏状态
const board = ref<number[]>(new Array(BOARD_WIDTH * BOARD_HEIGHT).fill(0))
const score = ref(0)
const lines = ref(0)
const level = ref(1)
const gameStarted = ref(false)
const gameOver = ref(false)
const isPaused = ref(false)

// 当前方块
const currentPiece = ref<{
  shape: number[][]
  x: number
  y: number
  color: number
} | null>(null)

// 下一个方块
const nextPieceShape = ref<number[][] | null>(null)
const nextPieceColor = ref(0)

// 下落控制
let lastDropTime = 0
let animationFrameId: number | null = null

// 计算当前方块的位置
const currentPiecePositions = computed(() => {
  if (!currentPiece.value) return []
  const positions = []
  for (let y = 0; y < currentPiece.value.shape.length; y++) {
    for (let x = 0; x < currentPiece.value.shape[y].length; x++) {
      if (currentPiece.value.shape[y][x] !== 0) {
        positions.push({
          x: currentPiece.value.x + x,
          y: currentPiece.value.y + y
        })
      }
    }
  }
  return positions
})

// 计算幽灵方块位置（落点预览）
const ghostPositions = computed(() => {
  if (!currentPiece.value) return []
  
  let ghostY = currentPiece.value.y
  // 向下查找直到碰撞
  while (canMove(currentPiece.value.shape, currentPiece.value.x, ghostY + 1)) {
    ghostY++
  }
  
  // 如果幽灵位置和当前位置相同，不显示
  if (ghostY === currentPiece.value.y) return []
  
  const positions = []
  for (let y = 0; y < currentPiece.value.shape.length; y++) {
    for (let x = 0; x < currentPiece.value.shape[y].length; x++) {
      if (currentPiece.value.shape[y][x] !== 0) {
        positions.push({
          x: currentPiece.value.x + x,
          y: ghostY + y
        })
      }
    }
  }
  return positions
})

// 获取当前下落间隔
const dropInterval = computed(() => {
  return Math.max(100, DROP_INTERVAL_BASE - (level.value - 1) * 80)
})

// 初始化游戏
function initGame() {
  board.value = new Array(BOARD_WIDTH * BOARD_HEIGHT).fill(0)
  score.value = 0
  lines.value = 0
  level.value = 1
  gameOver.value = false
  isPaused.value = false
  currentPiece.value = null
  nextPieceShape.value = null
  nextPieceColor.value = 0
}

// 生成随机方块
function generatePiece() {
  const idx = Math.floor(Math.random() * SHAPES.length)
  const { shape, color } = SHAPES[idx]
  return {
    shape: shape.map(row => [...row]),
    x: Math.floor(BOARD_WIDTH / 2) - Math.floor(shape[0].length / 2),
    y: 0,
    color
  }
}

// 生成下一个方块
function prepareNextPiece() {
  const piece = generatePiece()
  nextPieceShape.value = piece.shape
  nextPieceColor.value = piece.color
}

// 生成当前方块
function spawnPiece() {
  if (!nextPieceShape.value) {
    prepareNextPiece()
  }
  
  currentPiece.value = {
    shape: nextPieceShape.value!.map(row => [...row]),
    x: Math.floor(BOARD_WIDTH / 2) - Math.floor(nextPieceShape.value![0].length / 2),
    y: 0,
    color: nextPieceColor.value
  }
  
  // 准备下一个
  prepareNextPiece()
  
  // 检查是否可以放置
  if (!canMove(currentPiece.value.shape, currentPiece.value.x, currentPiece.value.y)) {
    endGame()
  }
}

// 检查是否可以移动
function canMove(shape: number[][], x: number, y: number): boolean {
  for (let py = 0; py < shape.length; py++) {
    for (let px = 0; px < shape[py].length; px++) {
      if (shape[py][px] !== 0) {
        const newX = x + px
        const newY = y + py
        
        // 边界检查
        if (newX < 0 || newX >= BOARD_WIDTH || newY >= BOARD_HEIGHT) return false
        
        // 碰撞检查
        if (newY >= 0 && board.value[newY * BOARD_WIDTH + newX] !== 0) return false
      }
    }
  }
  return true
}

// 固定当前方块到棋盘
function lockPiece() {
  if (!currentPiece.value) return
  
  for (let y = 0; y < currentPiece.value.shape.length; y++) {
    for (let x = 0; x < currentPiece.value.shape[y].length; x++) {
      if (currentPiece.value.shape[y][x] !== 0) {
        const boardY = currentPiece.value.y + y
        const boardX = currentPiece.value.x + x
        if (boardY >= 0) {
          board.value[boardY * BOARD_WIDTH + boardX] = currentPiece.value.color
        }
      }
    }
  }
}

// 消除满行
function clearLines() {
  let cleared = 0
  
  for (let y = BOARD_HEIGHT - 1; y >= 0; y--) {
    let isFull = true
    for (let x = 0; x < BOARD_WIDTH; x++) {
      if (board.value[y * BOARD_WIDTH + x] === 0) {
        isFull = false
        break
      }
    }
    
    if (isFull) {
      // 删除该行，顶部添加新空行
      board.value.splice(y * BOARD_WIDTH, BOARD_WIDTH)
      board.value.unshift(...new Array(BOARD_WIDTH).fill(0))
      cleared++
      y++ // 重新检查当前行
    }
  }
  
  if (cleared > 0) {
    lines.value += cleared
    score.value += cleared * 100 * level.value
    level.value = Math.floor(lines.value / 10) + 1
  }
}

// 旋转方块
function rotate() {
  if (!currentPiece.value || isPaused.value) return
  
  const rotated = currentPiece.value.shape[0].map((_, i) =>
    currentPiece!.value!.shape.map(row => row[i]).reverse()
  )
  
  if (canMove(rotated, currentPiece.value.x, currentPiece.value.y)) {
    currentPiece.value.shape = rotated
  }
}

// 移动方块
function move(dx: number, dy: number): boolean {
  if (!currentPiece.value || isPaused.value) return false
  
  if (canMove(currentPiece.value.shape, currentPiece.value.x + dx, currentPiece.value.y + dy)) {
    currentPiece.value.x += dx
    currentPiece.value.y += dy
    return true
  }
  return false
}

function moveLeft() { move(-1, 0) }
function moveRight() { move(1, 0) }

// 软降（加速下落一格）
function softDrop() {
  if (!move(0, 1)) {
    lockPiece()
    clearLines()
    spawnPiece()
  }
}

// 硬降（直接落到底部）
function hardDrop() {
  if (!currentPiece.value || isPaused.value) return
  
  while (move(0, 1)) {}
  lockPiece()
  clearLines()
  spawnPiece()
}

// 游戏主循环
function gameLoop(timestamp: number) {
  if (!gameStarted.value || gameOver.value) return
  
  if (!isPaused.value) {
    // 自动下落
    if (timestamp - lastDropTime >= dropInterval.value) {
      if (!move(0, 1)) {
        lockPiece()
        clearLines()
        spawnPiece()
      }
      lastDropTime = timestamp
    }
  }
  
  animationFrameId = requestAnimationFrame(gameLoop)
}

// 暂停/继续
function togglePause() {
  if (!gameStarted.value || gameOver.value) return
  isPaused.value = !isPaused.value
}

// 结束游戏
function endGame() {
  gameOver.value = true
  isPaused.value = false
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
}

// 开始游戏
function startGame() {
  initGame()
  gameStarted.value = true
  prepareNextPiece()
  spawnPiece()
  lastDropTime = performance.now()
  animationFrameId = requestAnimationFrame(gameLoop)
}

// 重新开始
function restartGame() {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
  startGame()
}

// 键盘控制
function handleKeydown(e: KeyboardEvent) {
  if (!gameStarted.value || gameOver.value) return
  
  switch (e.key) {
    case 'ArrowLeft':
      e.preventDefault()
      moveLeft()
      break
    case 'ArrowRight':
      e.preventDefault()
      moveRight()
      break
    case 'ArrowDown':
      e.preventDefault()
      softDrop()
      break
    case 'ArrowUp':
      e.preventDefault()
      rotate()
      break
    case ' ':
      e.preventDefault()
      hardDrop()
      break
    case 'p':
    case 'P':
      togglePause()
      break
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.tetris-game {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
  background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%);
  min-height: 100%;
}

.game-title {
  color: #ff00ff;
  text-shadow: 0 0 20px #ff00ff, 0 0 40px #ff00ff;
  font-size: 1.8em;
  margin-bottom: 10px;
  letter-spacing: 3px;
}

.game-layout {
  display: flex;
  gap: 15px;
  align-items: flex-start;
}

.side-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100px;
}

.preview-box {
  background: rgba(255, 0, 255, 0.1);
  border: 1px solid #ff00ff;
  border-radius: 8px;
  padding: 10px;
  text-align: center;
}

.box-label {
  display: block;
  color: #fff;
  font-size: 0.8em;
  margin-bottom: 8px;
}

.next-piece {
  display: flex;
  flex-direction: column;
  gap: 2px;
  justify-content: center;
  align-items: center;
  min-height: 60px;
}

.next-row {
  display: flex;
  gap: 2px;
}

.next-cell {
  width: 15px;
  height: 15px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.05);
}

.next-cell.filled {
  box-shadow: 0 0 5px currentColor;
}

.info-box {
  background: rgba(255, 0, 255, 0.1);
  border: 1px solid #ff00ff;
  border-radius: 8px;
  padding: 10px;
  text-align: center;
}

.info-label {
  display: block;
  color: #888;
  font-size: 0.7em;
  margin-bottom: 4px;
}

.info-value {
  display: block;
  color: #ff00ff;
  font-size: 1.5em;
  font-weight: bold;
}

.pause-btn {
  background: rgba(255, 0, 255, 0.2);
  border: 2px solid #ff00ff;
  color: #ff00ff;
  border-radius: 8px;
  padding: 10px;
  font-size: 1.2em;
  cursor: pointer;
  transition: all 0.3s;
}

.pause-btn:hover {
  background: #ff00ff;
  color: #0a0a0a;
}

.game-area {
  position: relative;
  padding: 3px;
  background: linear-gradient(45deg, #ff00ff, #ff0066);
  border-radius: 8px;
}

.board {
  display: grid;
  grid-template-columns: repeat(10, 22px);
  grid-template-rows: repeat(20, 22px);
  gap: 1px;
  background: #1a1a1a;
  padding: 4px;
  border-radius: 5px;
  position: relative;
}

.board.paused {
  opacity: 0.5;
}

.cell {
  width: 22px;
  height: 22px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 2px;
}

.cell.filled {
  box-shadow: 0 0 8px currentColor;
}

.piece-cell,
.ghost-cell {
  position: absolute;
  width: 22px;
  height: 22px;
  border-radius: 2px;
  pointer-events: none;
}

.piece-cell {
  box-shadow: 0 0 10px currentColor;
  animation: pieceGlow 1s ease-in-out infinite alternate;
}

.ghost-cell {
  opacity: 0.25;
  border: 1px dashed currentColor;
}

@keyframes pieceGlow {
  from { box-shadow: 0 0 5px currentColor; }
  to { box-shadow: 0 0 15px currentColor; }
}

.color-1 { background: #00f5ff; }
.color-2 { background: #ffcc00; }
.color-3 { background: #ff00ff; }
.color-4 { background: #00ff88; }
.color-5 { background: #ff0066; }
.color-6 { background: #9b59b6; }
.color-7 { background: #e74c3c; }

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 5px;
  z-index: 10;
}

.overlay h2 {
  color: #ff00ff;
  font-size: 1.5em;
  margin-bottom: 10px;
  text-shadow: 0 0 20px #ff00ff;
}

.final-score {
  color: #00f5ff;
  font-size: 1.2em;
  margin-bottom: 15px;
}

.overlay button {
  padding: 12px 30px;
  background: transparent;
  border: 2px solid #ff00ff;
  color: #ff
00ff;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1em;
  transition: all 0.3s;
}

.overlay button:hover {
  background: #ff00ff;
  color: #0a0a0a;
}

.pause-overlay {
  background: rgba(0, 0, 0, 0.7);
}

.game-tip {
  margin-top: 10px;
  color: #888;
  font-size: 0.85em;
}

.desktop-only {
  display: block;
}

/* 移动端触摸控制 */
.mobile-controls {
  display: none;
  width: 100%;
  max-width: 400px;
  margin-top: 15px;
  justify-content: space-between;
  padding: 0 20px;
}

.control-group {
  display: flex;
  gap: 15px;
}

.control-group.left {
  flex-direction: column;
}

.control-group.right {
  flex-direction: row;
  align-items: center;
}

.control-btn {
  padding: 18px 22px;
  background: rgba(255, 0, 255, 0.15);
  border: 2px solid #ff00ff;
  color: #ff00ff;
  border-radius: 12px;
  font-size: 1.5em;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 55px;
  text-align: center;
}

.control-btn:active {
  background: #ff00ff;
  color: #0a0a0a;
  transform: scale(0.95);
}

.control-btn.rotate {
  font-size: 2em;
  padding: 15px 20px;
}

.control-btn.left,
.control-btn.right {
  font-size: 2em;
  padding: 20px 25px;
}

@media (max-width: 768px) {
  .game-title {
    font-size: 1.5em;
  }
  
  .game-layout {
    flex-direction: row;
    gap: 10px;
  }
  
  .side-panel {
    width: 80px;
  }
  
  .next-cell {
    width: 12px;
    height: 12px;
  }
  
  .board {
    grid-template-columns: repeat(10, 18px);
    grid-template-rows: repeat(20, 18px);
  }
  
  .cell,
  .piece-cell,
  .ghost-cell {
    width: 18px;
    height: 18px;
  }
  
  .desktop-only {
    display: none;
  }
  
  .mobile-controls {
    display: flex;
  }
}
</style>
