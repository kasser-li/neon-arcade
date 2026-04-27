<template>
  <div class="game-2048">
    <h1 class="game-title">NEON 2048</h1>
    
    <div class="game-header">
      <div class="score-box">
        <span class="score-label">得分</span>
        <span class="score-value">{{ score }}</span>
      </div>
      <div class="score-box">
        <span class="score-label">最高分</span>
        <span class="score-value">{{ bestScore }}</span>
      </div>
      <button class="new-game-btn" @click="restartGame">新游戏</button>
    </div>
    
    <div class="game-board">
      <div class="board-container">
        <div
          v-for="(cell, index) in flatBoard"
          :key="index"
          class="cell"
          :class="[`tile-${cell}`]"
        >
          {{ cell !== 0 ? cell : '' }}
        </div>
      </div>
      
      <div v-if="gameOver" class="overlay">
        <h2>游戏结束</h2>
        <button @click="restartGame">再试一次</button>
      </div>
      
      <div v-if="won" class="overlay">
        <h2>🎉 达成 2048！</h2>
        <button @click="continueGame">继续游戏</button>
      </div>
    </div>
    
    <p class="game-tip">🎮 操作：使用方向键 ↑ ↓ ← → 滑动方块</p>
    
    <!-- 移动端触摸控制 -->
    <div class="touch-controls" v-if="!gameOver && !won">
      <div class="control-row">
        <button class="touch-btn" @click="move('up')">↑ 上</button>
      </div>
      <div class="control-row">
        <button class="touch-btn" @click="move('left')">← 左</button>
        <button class="touch-btn" @click="move('down')">↓ 下</button>
        <button class="touch-btn" @click="move('right')">右 →</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const BOARD_SIZE = 4

const board = ref<number[][]>([
  [0, 0, 0, 0],
  [0, 0, 0, 0],
  [0, 0, 0, 0],
  [0, 0, 0, 0]
])

const score = ref(0)
const bestScore = ref(0)
const gameOver = ref(false)
const won = ref(false)
const canContinue = ref(false)

const flatBoard = computed(() => board.value.flat())

function initGame() {
  board.value = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
  ]
  score.value = 0
  gameOver.value = false
  won.value = false
  canContinue.value = false
  addRandomTile()
  addRandomTile()
}

function addRandomTile() {
  const emptyCells: { x: number; y: number }[] = []
  
  for (let y = 0; y < BOARD_SIZE; y++) {
    for (let x = 0; x < BOARD_SIZE; x++) {
      if (board.value[y][x] === 0) {
        emptyCells.push({ x, y })
      }
    }
  }
  
  if (emptyCells.length > 0) {
    const { x, y } = emptyCells[Math.floor(Math.random() * emptyCells.length)]
    board.value[y][x] = Math.random() < 0.9 ? 2 : 4
  }
}

function move(direction: string) {
  if (gameOver.value) return
  
  const newBoard = board.value.map(row => [...row])
  let moved = false
  let merged = new Set<string>()
  
  const getCell = (x: number, y: number) => newBoard[y][x]
  const setCell = (x: number, y: number, value: number) => { newBoard[y][x] = value }
  
  const traverse = (callback: (x: number, y: number) => void) => {
    if (direction === 'up' || direction === 'down') {
      for (let x = 0; x < BOARD_SIZE; x++) {
        for (let y = 0; y < BOARD_SIZE; y++) {
          callback(x, direction === 'up' ? y : BOARD_SIZE - 1 - y)
        }
      }
    } else {
      for (let y = 0; y < BOARD_SIZE; y++) {
        for (let x = 0; x < BOARD_SIZE; x++) {
          callback(direction === 'left' ? x : BOARD_SIZE - 1 - x, y)
        }
      }
    }
  }
  
  const getNextPos = (x: number, y: number) => {
    switch (direction) {
      case 'up': return { x, y: y - 1 }
      case 'down': return { x, y: y + 1 }
      case 'left': return { x: x - 1, y }
      case 'right': return { x: x + 1, y }
      default: return { x, y }
    }
  }
  
  const isValid = (x: number, y: number) => x >= 0 && x < BOARD_SIZE && y >= 0 && y < BOARD_SIZE
  
  traverse((x, y) => {
    if (getCell(x, y) === 0) return
    
    let cx = x
    let cy = y
    let value = getCell(x, y)
    
    while (true) {
      const next = getNextPos(cx, cy)
      if (!isValid(next.x, next.y)) break
      
      const nextValue = getCell(next.x, next.y)
      const key = `${next.x},${next.y}`
      
      if (nextValue === 0) {
        setCell(cx, cy, 0)
        setCell(next.x, next.y, value)
        cx = next.x
        cy = next.y
        moved = true
      } else if (nextValue === value && !merged.has(key)) {
        setCell(cx, cy, 0)
        setCell(next.x, next.y, value * 2)
        score.value += value * 2
        if (score.value > bestScore.value) {
          bestScore.value = score.value
        }
        merged.add(key)
        moved = true
        
        if (value * 2 === 2048 && !canContinue.value) {
          won.value = true
        }
        break
      } else {
        break
      }
    }
  })
  
  if (moved) {
    board.value = newBoard
    addRandomTile()
    checkGameOver()
  }
}

function checkGameOver() {
  for (let y = 0; y < BOARD_SIZE; y++) {
    for (let x = 0; x < BOARD_SIZE; x++) {
      if (board.value[y][x] === 0) return
      
      const current = board.value[y][x]
      if (x < BOARD_SIZE - 1 && board.value[y][x + 1] === current) return
      if (y < BOARD_SIZE - 1 && board.value[y + 1][x] === current) return
    }
  }
  
  gameOver.value = true
}

function restartGame() {
  initGame()
}

function continueGame() {
  won.value = false
  canContinue.value = true
}

function handleKeydown(e: KeyboardEvent) {
  if (won.value && !canContinue.value) return
  
  switch (e.key) {
    case 'ArrowUp':
      e.preventDefault()
      move('up')
      break
    case 'ArrowDown':
      e.preventDefault()
      move('down')
      break
    case 'ArrowLeft':
      e.preventDefault()
      move('left')
      break
    case 'ArrowRight':
      e.preventDefault()
      move('right')
      break
  }
}

onMounted(() => {
  initGame()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.game-2048 {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: #0a0a0a;
  min-height: 100%;
}

.game-title {
  color: #ffcc00;
  text-shadow: 0 0 20px #ffcc00, 0 0 40px #ffcc00;
  font-size: 2em;
  margin-bottom: 15px;
  letter-spacing: 5px;
}

.game-header {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  align-items: center;
}

.score-box {
  background: rgba(255, 204, 0, 0.1);
  border: 1px solid #ffcc00;
  border-radius: 10px;
  padding: 10px 20px;
  text-align: center;
  box-shadow: 0 0 15px rgba(255, 204, 0, 0.3);
}

.score-label {
  display: block;
  color: #888;
  font-size: 0.8em;
  margin-bottom: 5px;
}

.score-value {
  display: block;
  color: #ffcc00;
  font-size: 1.5em;
  font-weight: bold;
}

.new-game-btn {
  padding: 10px 25px;
  background: transparent;
  border: 2px solid #ff6600;
  color: #ff6600;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9em;
}

.new-game-btn:hover {
  background: #ff6600;
  color: #0a0a0a;
}

.game-board {
  position: relative;
  padding: 10px;
  background: linear-gradient(45deg, #ffcc00, #ff6600, #ffcc00);
  border-radius: 10px;
}

.board-container {
  display: grid;
  grid-template-columns: repeat(4, 80px);
  grid-template-rows: repeat(4, 80px);
  gap: 10px;
  background: #1a1a1a;
  padding: 10px;
  border-radius: 8px;
}

.cell {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5em;
  font-weight: bold;
  color: #fff;
  transition: all 0.15s;
}

.tile-2 { background: #eee4da; color: #776e65; }
.tile-4 { background: #ede0c8; color: #776e65; }
.tile-8 { background: #f2b179; color: #f9f6f2; }
.tile-16 { background: #f59563; color: #f9f6f2; }
.tile-32 { background: #f67c5f; color: #f9f6f2; }
.tile-64 { background: #f65e3b; color: #f9f6f2; }
.tile-128 { background: #edcf72; color: #f9f6f2; box-shadow: 0 0 10px #edcf72; }
.tile-256 { background: #edcc61; color: #f9f6f2; box-shadow: 0 0 10px #edcc61; }
.tile-512 { background: #edc850; color: #f9f6f2; box-shadow: 0 0 10px #edc850; }
.tile-1024 { background: #edc53f; color: #f9f6f2; box-shadow: 0 0 15px #edc53f; }
.tile-2048 { background: #edc22e; color: #f9f6f2; box-shadow: 0 0 20px #edc22e; }

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
  color: #ffcc00;
  font-size: 1.5em;
  margin-bottom: 15px;
  text-shadow: 0 0 20px #ffcc00;
}

.overlay button {
  padding: 10px 25px;
  background: transparent;
  border: 2px solid #ffcc00;
  color: #ffcc00;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s;
}

.overlay button:hover {
  background: #ffcc00;
  color: #0a0a0a;
}

.game-tip {
  margin-top: 15px;
  color: #888;
  font-size: 0.9em;
}
</style>

.touch-controls {
  display: none;
  margin-top: 20px;
}

.control-row {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 10px;
}

.touch-btn {
  padding: 15px 25px;
  background: rgba(255, 204, 0, 0.2);
  border: 2px solid #ffcc00;
  color: #ffcc00;
  border-radius: 10px;
  font-size: 1em;
  cursor: pointer;
  transition: all 0.3s;
  min-width: 60px;
}

.touch-btn:active {
  background: #ffcc00;
  color: #0a0a0a;
}

@media (max-width: 768px) {
  .game-header {
    flex-wrap: wrap;
  }
  
  .board-container {
    grid-template-columns: repeat(4, 60px);
    grid-template-rows: repeat(4, 60px);
    gap: 8px;
  }
  
  .cell {
    width: 60px;
    height: 60px;
    font-size: 1.2em;
  }
  
  .touch-controls {
    display: block;
  }
}
