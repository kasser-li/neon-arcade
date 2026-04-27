<template>
  <div class="sudoku-game">
    <h1 class="game-title">NEON SUDOKU</h1>
    
    <div class="game-header">
      <div class="difficulty-selector">
        <button 
          v-for="diff in difficulties" 
          :key="diff.level"
          :class="['diff-btn', { active: selectedDiff === diff.level }]"
          @click="changeDifficulty(diff.level)"
        >
          {{ diff.label }}
        </button>
      </div>
      
      <div class="game-stats">
        <div class="stat">
          <span class="stat-label">时间</span>
          <span class="stat-value">{{ formatTime(timer) }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">提示</span>
          <span class="stat-value">{{ hints }}</span>
        </div>
      </div>
    </div>
    
    <div class="game-board">
      <div 
        v-for="(cell, index) in flatBoard" 
        :key="index"
        class="cell"
        :class="{
          'is-fixed': cell.isFixed,
          'is-selected': selectedCell === index,
          'is-same-number': selectedNumber !== null && cell.value === selectedNumber && cell.value !== 0,
          'is-related': isRelatedCell(index),
          'is-error': cell.isError
        }"
        @click="selectCell(index)"
      >
        {{ cell.value !== 0 ? cell.value : '' }}
      </div>
    </div>
    
    <div class="number-pad">
      <button 
        v-for="num in 9" 
        :key="num"
        class="num-btn"
        @click="inputNumber(num)"
      >
        {{ num }}
      </button>
      <button class="num-btn erase" @click="inputNumber(0)">⌫</button>
    </div>
    
    <div class="game-controls">
      <button class="control-btn" @click="useHint">💡 提示</button>
      <button class="control-btn" @click="checkSolution">✓ 检查</button>
      <button class="control-btn" @click="newGame">🔄 新游戏</button>
    </div>
    
    <div v-if="gameWon" class="overlay">
      <h2>🎉 恭喜通关！</h2>
      <p>用时: {{ formatTime(timer) }}</p>
      <button @click="newGame">再来一局</button>
    </div>
    
    <p class="game-tip">🎮 点击格子选择，然后点击数字填入</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const difficulties = [
  { level: 'easy', label: '简单', emptyCells: 30 },
  { level: 'medium', label: '中等', emptyCells: 40 },
  { level: 'hard', label: '困难', emptyCells: 50 }
]

const selectedDiff = ref('medium')
const board = ref<number[][]>(Array(9).fill(null).map(() => Array(9).fill(0)))
const solution = ref<number[][]>(Array(9).fill(null).map(() => Array(9).fill(0)))
const fixedCells = ref<boolean[][]>(Array(9).fill(null).map(() => Array(9).fill(false)))
const selectedCell = ref<number | null>(null)
const errors = ref<Set<number>>(new Set())
const timer = ref(0)
const hints = ref(3)
const gameWon = ref(false)

let timerInterval: number | null = null

const flatBoard = computed(() => {
  const result = []
  for (let row = 0; row < 9; row++) {
    for (let col = 0; col < 9; col++) {
      result.push({
        value: board.value[row][col],
        isFixed: fixedCells.value[row][col],
        isError: errors.value.has(row * 9 + col)
      })
    }
  }
  return result
})

// 当前选中的数字
const selectedNumber = computed(() => {
  if (selectedCell.value === null) return null
  return flatBoard.value[selectedCell.value].value
})

// 判断是否是相关格子（同行、同列、同宫）
function isRelatedCell(index: number) {
  if (selectedCell.value === null) return false
  
  const selectedRow = Math.floor(selectedCell.value / 9)
  const selectedCol = selectedCell.value % 9
  const selectedBoxRow = Math.floor(selectedRow / 3) * 3
  const selectedBoxCol = Math.floor(selectedCol / 3) * 3
  
  const cellRow = Math.floor(index / 9)
  const cellCol = index % 9
  const cellBoxRow = Math.floor(cellRow / 3) * 3
  const cellBoxCol = Math.floor(cellCol / 3) * 3
  
  // 同行、同列或同宫
  return (
    selectedRow === cellRow ||
    selectedCol === cellCol ||
    (selectedBoxRow === cellBoxRow && selectedBoxCol === cellBoxCol)
  )
}

function formatTime(seconds: number) {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

function isValid(board: number[][], row: number, col: number, num: number) {
  // 检查行
  for (let x = 0; x < 9; x++) {
    if (board[row][x] === num) return false
  }
  
  // 检查列
  for (let x = 0; x < 9; x++) {
    if (board[x][col] === num) return false
  }
  
  // 检查3x3方格
  const startRow = row - row % 3
  const startCol = col - col % 3
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
      if (board[i + startRow][j + startCol] === num) return false
    }
  }
  
  return true
}

function solveSudoku(board: number[][]) {
  for (let row = 0; row < 9; row++) {
    for (let col = 0; col < 9; col++) {
      if (board[row][col] === 0) {
        for (let num = 1; num <= 9; num++) {
          if (isValid(board, row, col, num)) {
            board[row][col] = num
            if (solveSudoku(board)) return true
            board[row][col] = 0
          }
        }
        return false
      }
    }
  }
  return true
}

function generateBoard() {
  // 生成完整解答
  const newBoard = Array(9).fill(null).map(() => Array(9).fill(0))
  
  // 随机填充一些数字作为种子
  for (let i = 0; i < 10; i++) {
    const row = Math.floor(Math.random() * 9)
    const col = Math.floor(Math.random() * 9)
    const num = Math.floor(Math.random() * 9) + 1
    if (isValid(newBoard, row, col, num)) {
      newBoard[row][col] = num
    }
  }
  
  solveSudoku(newBoard)
  solution.value = newBoard.map(row => [...row])
  
  // 复制到游戏板
  board.value = newBoard.map(row => [...row])
  
  // 根据难度移除数字
  const diff = difficulties.find(d => d.level === selectedDiff.value) || difficulties[1]
  let removed = 0
  
  fixedCells.value = Array(9).fill(null).map(() => Array(9).fill(true))
  
  while (removed < diff.emptyCells) {
    const row = Math.floor(Math.random() * 9)
    const col = Math.floor(Math.random() * 9)
    
    if (board.value[row][col] !== 0) {
      board.value[row][col] = 0
      fixedCells.value[row][col] = false
      removed++
    }
  }
}

function selectCell(index: number) {
  selectedCell.value = index
}

function inputNumber(num: number) {
  if (selectedCell.value === null) return
  
  const row = Math.floor(selectedCell.value / 9)
  const col = selectedCell.value % 9
  
  if (!fixedCells.value[row][col]) {
    board.value[row][col] = num
    errors.value.delete(selectedCell.value)
    checkWin()
  }
}

function useHint() {
  if (hints.value <= 0 || selectedCell.value === null) return
  
  const row = Math.floor(selectedCell.value / 9)
  const col = selectedCell.value % 9
  
  if (!fixedCells.value[row][col] && board.value[row][col] !== solution.value[row][col]) {
    board.value[row][col] = solution.value[row][col]
    hints.value--
    errors.value.delete(selectedCell.value)
    checkWin()
  }
}

function checkSolution() {
  errors.value.clear()
  
  for (let row = 0; row < 9; row++) {
    for (let col = 0; col < 9; col++) {
      if (board.value[row][col] !== 0 && board.value[row][col] !== solution.value[row][col]) {
        errors.value.add(row * 9 + col)
      }
    }
  }
}

function checkWin() {
  for (let row = 0; row < 9; row++) {
    for (let col = 0; col < 9; col++) {
      if (board.value[row][col] !== solution.value[row][col]) {
        return false
      }
    }
  }
  
  gameWon.value = true
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  return true
}

function changeDifficulty(level: string) {
  selectedDiff.value = level
  newGame()
}

function newGame() {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
  
  gameWon.value = false
  timer.value = 0
  hints.value = 3
  errors.value.clear()
  selectedCell.value = null
  
  generateBoard()
  
  timerInterval = window.setInterval(() => {
    timer.value++
  }, 1000)
}

onMounted(() => {
  newGame()
})

onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
})
</script>

<style scoped>
.sudoku-game {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: #0a0a0a;
  min-height: 100%;
}

.game-title {
  color: #9ca3af;
  text-shadow: 0 0 10px rgba(156, 163, 175, 0.5);
  font-size: 2em;
  margin-bottom: 15px;
  letter-spacing: 5px;
}

.game-header {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
  align-items: center;
}

.difficulty-selector {
  display: flex;
  gap: 10px;
}

.diff-btn {
  padding: 8px 20px;
  background: transparent;
  border: 1px solid #6b7280;
  color: #9ca3af;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.diff-btn.active,
.diff-btn:hover {
  background: rgba(156, 163, 175, 0.4);
  color: #fff;
}

.game-stats {
  display: flex;
  gap: 20px;
}

.stat {
  text-align: center;
  padding: 8px 15px;
  background: rgba(107, 114, 128, 0.1);
  border: 1px solid #6b7280;
  border-radius: 10px;
}

.stat-label {
  display: block;
  color: #888;
  font-size: 0.8em;
}

.stat-value {
  display: block;
  color: #9ca3af;
  font-size: 1.3em;
  font-weight: bold;
}

.game-board {
  display: grid;
  grid-template-columns: repeat(9, 40px);
  grid-template-rows: repeat(9, 40px);
  gap: 1px;
  padding: 3px;
  background: linear-gradient(45deg, #374151, #4b5563, #374151);
  border-radius: 10px;
}

.cell {
  width: 40px;
  height: 40px;
  background: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2em;
  font-weight: bold;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.cell:nth-child(3n):not(:nth-child(9n)) {
  border-right: 2px solid #4b5563;
}

.cell:nth-child(n+19):nth-child(-n+27),
.cell:nth-child(n+46):nth-child(-n+54) {
  border-bottom: 2px solid #4b5563;
}

.cell.is-fixed {
  color: #9ca3af;
  background: rgba(156, 163, 175, 0.15);
}

.cell.is-selected {
  background: rgba(156, 163, 175, 0.3);
  box-shadow: 0 0 10px rgba(156, 163, 175, 0.5);
  transform: scale(1.05);
  z-index: 10;
}

.cell.is-related {
  background: rgba(156, 163, 175, 0.12);
}

.cell.is-same-number {
  background: rgba(156, 163, 175, 0.4);
  color: #fff;
  font-weight: bold;
}

.cell.is-error {
  color: #fff;
  background: rgba(255, 68, 68, 0.4);
  text-shadow: 0 0 8px #ff4444;
}

.number-pad {
  display: flex;
  gap: 8px;
  margin-top: 20px;
  flex-wrap: wrap;
  justify-content: center;
}

.num-btn {
  width: 45px;
  height: 45px;
  background: rgba(156, 163, 175, 0.15);
  border: 1px solid #6b7280;
  color: #9ca3af;
  border-radius: 8px;
  font-size: 1.2em;
  cursor: pointer;
  transition: all 0.2s;
}

.num-btn:hover,
.num-btn:active {
  background: rgba(156, 163, 175, 0.4);
  color: #fff;
}

.num-btn.erase {
  border-color: #4b5563;
  color: #4b5563;
}

.num-btn.erase:hover {
  background: #4b5563;
  color: #fff;
}

.game-controls {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

.control-btn {
  padding: 10px 25px;
  background: transparent;
  border: 1px solid #6b7280;
  color: #9ca3af;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s;
}

.control-btn:hover {
  background: rgba(156, 163, 175, 0.4);
  color: #fff;
}

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
  color: #9ca3af;
  font-size: 2em;
  margin-bottom: 15px;
  text-shadow: 0 0 20px #6b7280;
}

.overlay p {
  color: #fff;
  font-size: 1.2em;
  margin: 5px 0;
}

.overlay button {
  padding: 15px 40px;
  margin-top: 20px;
  background: transparent;
  border: 3px solid #6b7280;
  color: #9ca3af;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 1.1em;
}

.overlay button:hover {
  background: rgba(156, 163, 175, 0.4);
  color: #fff;
}

.game-tip {
  margin-top: 15px;
  color: #888;
  font-size: 0.9em;
}

@media (max-width: 768px) {
  .game-board {
    grid-template-columns: repeat(9, 35px);
    grid-template-rows: repeat(9, 35px);
  }
  
  .cell {
    width: 35px;
    height: 35px;
    font-size: 1em;
  }
  
  .num-btn {
    width: 40px;
    height: 40px;
  }
}
</style>
