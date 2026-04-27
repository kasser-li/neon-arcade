<template>
  <div class="match3-game">
    <!-- 顶部信息栏 -->
    <div class="top-bar">
      <button class="back-btn" @click="goBack">← 返回</button>
      <div class="score-info">
        <div class="score-item">
          <span class="label">分数</span>
          <span class="value">{{ score }}</span>
        </div>
        <div class="score-item">
          <span class="label">最高分</span>
          <span class="value">{{ highScore }}</span>
        </div>
        <div class="score-item">
          <span class="label">金币</span>
          <span class="value coins">{{ coins }}</span>
        </div>
      </div>
    </div>
    
    <!-- 道具栏 -->
    <div class="powerup-bar">
      <button 
        v-for="powerUp in availablePowerUps" 
        :key="powerUp.id"
        class="powerup-btn"
        :class="{ 'active': activePowerUp === powerUp.id, 'disabled': shopStore.getPowerUpCount(powerUp.id) <= 0 }"
        @click="selectPowerUp(powerUp.id)"
        :disabled="shopStore.getPowerUpCount(powerUp.id) <= 0 || isProcessing"
      >
        <span class="powerup-icon">{{ powerUp.icon }}</span>
        <span class="powerup-count">{{ shopStore.getPowerUpCount(powerUp.id) }}</span>
      </button>
      <button class="powerup-btn shop" @click="goToShop">
        🛒 商店
      </button>
    </div>
    
    <!-- 连击显示 - 绝对定位，不占用文档流 -->
    <div class="combo-overlay" v-if="combo > 1">
      <div class="combo-display">
        <span class="combo-text">COMBO x{{ combo }}</span>
        <span class="bonus">+{{ comboBonus }}</span>
      </div>
    </div>
    
    <!-- 游戏棋盘 -->
    <div class="game-board" ref="boardRef">
      <div 
        v-for="(cell, index) in flatBoard" 
        :key="index"
        class="cell"
        :class="[
          `color-${cell.type}`,
          { 
            'is-selected': selectedIndex === index,
            'is-matched': matchedIndices.has(index),
            'is-special': cell.special,
            'is-falling': fallingIndices.has(index),
            'is-bomb': cell.special === 'bomb',
            'is-rocket-h': cell.special === 'rocket_h',
            'is-rocket-v': cell.special === 'rocket_v',
            'is-rainbow': cell.special === 'rainbow',
            'is-swapping': swappingIndices && (swappingIndices.from === index || swappingIndices.to === index)
          }
        ]"
        :style="getCellStyle(index)"
        @mousedown="handleMouseDown(index)"
        @mouseup="handleMouseUp(index)"
        @mouseenter="handleMouseEnter(index)"
        @touchstart.prevent="handleTouchStart(index)"
        @touchmove.prevent="handleTouchMove($event, index)"
        @touchend.prevent="handleTouchEnd(index)"
      >
        <span v-if="cell.special" class="special-icon">{{ getSpecialIcon(cell.special) }}</span>
      </div>
    </div>
    
    <!-- 游戏结束 -->
    <div v-if="gameOver" class="overlay">
      <h2>游戏结束</h2>
      <p class="final-score">最终得分: {{ score }}</p>
      <p v-if="score === highScore" class="new-record">🎉 新纪录！</p>
      <button class="restart-btn" @click="restartGame">再来一局</button>
    </div>
    
    <!-- 提示 -->
    <p class="tip">点击两个相邻元素交换位置</p>
    <p class="tip">4连消=火箭 🚀 | 5连消=炸弹 💣 | T/L型=彩虹球 🌈</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMatch3ShopStore, POWER_UPS, type PowerUpType } from '../stores/match3Shop'

const router = useRouter()
const shopStore = useMatch3ShopStore()

// 道具系统
const coins = ref(0)
const activePowerUp = ref<PowerUpType | null>(null)
const earnedCoins = ref(0) // 本局获得的金币

const availablePowerUps = computed(() => POWER_UPS.filter(p => p.type === 'ingame'))

// 游戏配置
const BOARD_SIZE = 8
const CELL_TYPES = 6
const ANIMATION_DURATION = 200

// 特效类型
const SPECIAL = {
  BOMB: 'bomb',
  ROCKET_H: 'rocket_h',
  ROCKET_V: 'rocket_v',
  RAINBOW: 'rainbow'
}

// 单元格数据结构
interface Cell {
  type: number
  special: string | null
}

// 游戏状态
const board = ref<Cell[][]>([])
const selectedIndex = ref<number | null>(null)
const score = ref(0)
const highScore = ref(0)
const combo = ref(0)
const gameOver = ref(false)
const isProcessing = ref(false)
const matchedIndices = ref<Set<number>>(new Set())
const fallingIndices = ref<Set<number>>(new Set())

// 扁平化棋盘
const flatBoard = computed(() => {
  const result: Cell[] = []
  for (let row = 0; row < BOARD_SIZE; row++) {
    for (let col = 0; col < BOARD_SIZE; col++) {
      result.push(board.value[row]?.[col] || { type: 0, special: null })
    }
  }
  return result
})

// 连击奖励
const comboBonus = computed(() => {
  return combo.value * 10
})

// 初始化游戏
function initGame() {
  board.value = generateBoard()
  score.value = 0
  combo.value = 0
  gameOver.value = false
  selectedIndex.value = null
  matchedIndices.value.clear()
  fallingIndices.value.clear()
  
  // 确保没有初始匹配
  while (hasMatches().size > 0) {
    board.value = generateBoard()
  }
}

// 生成棋盘
function generateBoard(): Cell[][] {
  const newBoard: Cell[][] = []
  for (let row = 0; row < BOARD_SIZE; row++) {
    newBoard[row] = []
    for (let col = 0; col < BOARD_SIZE; col++) {
      newBoard[row][col] = {
        type: Math.floor(Math.random() * CELL_TYPES),
        special: null
      }
    }
  }
  return newBoard
}

// 查找所有匹配（返回匹配信息和特殊道具生成位置）
function findMatches(): { matches: Set<number>, specialCells: Map<number, string> } {
  const matches = new Set<number>()
  const specialCells = new Map<number, string>()
  
  // 检查横向
  for (let row = 0; row < BOARD_SIZE; row++) {
    let count = 1
    let startCol = 0
    for (let col = 1; col <= BOARD_SIZE; col++) {
      if (col < BOARD_SIZE && 
          board.value[row][col].type === board.value[row][col - 1].type && 
          board.value[row][col].type !== -1) {
        count++
      } else {
        if (count >= 3) {
          for (let i = startCol; i < startCol + count; i++) {
            matches.add(row * BOARD_SIZE + i)
          }
          // 生成特殊道具
          const centerIndex = row * BOARD_SIZE + Math.floor(startCol + count / 2)
          if (count === 4) {
            specialCells.set(centerIndex, SPECIAL.ROCKET_H)
          } else if (count >= 5) {
            specialCells.set(centerIndex, SPECIAL.BOMB)
          }
        }
        count = 1
        startCol = col
      }
    }
  }
  
  // 检查纵向
  for (let col = 0; col < BOARD_SIZE; col++) {
    let count = 1
    let startRow = 0
    for (let row = 1; row <= BOARD_SIZE; row++) {
      if (row < BOARD_SIZE && 
          board.value[row][col].type === board.value[row - 1][col].type && 
          board.value[row][col].type !== -1) {
        count++
      } else {
        if (count >= 3) {
          for (let i = startRow; i < startRow + count; i++) {
            matches.add(i * BOARD_SIZE + col)
          }
          // 生成特殊道具
          const centerIndex = Math.floor(startRow + count / 2) * BOARD_SIZE + col
          if (count === 4) {
            // 如果这个位置已经有横向火箭，升级为炸弹
            if (specialCells.has(centerIndex) && specialCells.get(centerIndex) === SPECIAL.ROCKET_H) {
              specialCells.set(centerIndex, SPECIAL.BOMB)
            } else {
              specialCells.set(centerIndex, SPECIAL.ROCKET_V)
            }
          } else if (count >= 5) {
            specialCells.set(centerIndex, SPECIAL.BOMB)
          }
        }
        count = 1
        startRow = row
      }
    }
  }
  
  // 检查T型和L型（生成彩虹球）
  checkTLShape(matches, specialCells)
  
  return { matches, specialCells }
}

// 检查T型和L型匹配
function checkTLShape(matches: Set<number>, specialCells: Map<number, string>) {
  for (let row = 0; row < BOARD_SIZE - 2; row++) {
    for (let col = 0; col < BOARD_SIZE - 2; col++) {
      const type = board.value[row][col].type
      if (type === -1) continue
      
      // 检查T型 (横向3个 + 纵向3个，交叉点在中间)
      // T型上: 横向3个，下方2个
      if (col + 2 < BOARD_SIZE && row + 2 < BOARD_SIZE) {
        if (board.value[row][col + 1].type === type && board.value[row][col + 2].type === type &&
            board.value[row + 1][col + 1].type === type && board.value[row + 2][col + 1].type === type) {
          const centerIndex = row * BOARD_SIZE + col + 1
          if (!specialCells.has(centerIndex)) {
            specialCells.set(centerIndex, SPECIAL.RAINBOW)
          }
        }
      }
      
      // T型下: 横向3个，上方2个
      if (col + 2 < BOARD_SIZE && row >= 2) {
        if (board.value[row][col + 1].type === type && board.value[row][col + 2].type === type &&
            board.value[row - 1][col + 1].type === type && board.value[row - 2][col + 1].type === type) {
          const centerIndex = row * BOARD_SIZE + col + 1
          if (!specialCells.has(centerIndex)) {
            specialCells.set(centerIndex, SPECIAL.RAINBOW)
          }
        }
      }
      
      // L型: 纵向3个 + 横向3个（拐角处）
      if (col + 2 < BOARD_SIZE && row + 2 < BOARD_SIZE) {
        if (board.value[row + 1][col].type === type && board.value[row + 2][col].type === type &&
            board.value[row + 2][col + 1].type === type && board.value[row + 2][col + 2].type === type) {
          const centerIndex = (row + 2) * BOARD_SIZE + col
          if (!specialCells.has(centerIndex)) {
            specialCells.set(centerIndex, SPECIAL.RAINBOW)
          }
        }
      }
    }
  }
}

// 检查是否有匹配（简化版，用于初始化和检查可移动）
function hasMatches(): Set<number> {
  const result = findMatches()
  return result.matches
}

// 滑动/拖拽相关状态
const isDragging = ref(false)
const dragStartIndex = ref<number | null>(null)
const dragCurrentIndex = ref<number | null>(null)
const dragStartTime = ref(0)
const DRAG_THRESHOLD = 200 // 超过200ms认为是拖拽，否则是点击
const hasDragged = ref(false)

// 交换动画状态
const swappingIndices = ref<{ from: number; to: number } | null>(null)

// 处理点击
function handleCellClick(index: number) {
  if (isProcessing.value || gameOver.value) return
  
  if (selectedIndex.value === null) {
    selectedIndex.value = index
  } else if (selectedIndex.value === index) {
    selectedIndex.value = null
  } else {
    const row1 = Math.floor(selectedIndex.value / BOARD_SIZE)
    const col1 = selectedIndex.value % BOARD_SIZE
    const row2 = Math.floor(index / BOARD_SIZE)
    const col2 = index % BOARD_SIZE
    
    const isAdjacent = (Math.abs(row1 - row2) === 1 && col1 === col2) ||
                       (Math.abs(col1 - col2) === 1 && row1 === row2)
    
    if (isAdjacent) {
      trySwap(selectedIndex.value, index)
    } else {
      selectedIndex.value = index
    }
  }
}

// 鼠标/触摸按下
function handleMouseDown(index: number) {
  if (isProcessing.value || gameOver.value) return
  isDragging.value = true
  hasDragged.value = false
  dragStartIndex.value = index
  dragCurrentIndex.value = index
  dragStartTime.value = Date.now()
}

function handleTouchStart(index: number) {
  handleMouseDown(index)
}

// 鼠标/触摸进入（滑动过程中）
function handleMouseEnter(index: number) {
  if (!isDragging.value || dragStartIndex.value === null) return
  dragCurrentIndex.value = index
  hasDragged.value = true
  
  // 检查是否滑动到相邻格子
  const row1 = Math.floor(dragStartIndex.value / BOARD_SIZE)
  const col1 = dragStartIndex.value % BOARD_SIZE
  const row2 = Math.floor(index / BOARD_SIZE)
  const col2 = index % BOARD_SIZE
  
  const isAdjacent = (Math.abs(row1 - row2) === 1 && col1 === col2) ||
                     (Math.abs(col1 - col2) === 1 && row1 === row2)
  
  if (isAdjacent && dragStartIndex.value !== index) {
    trySwap(dragStartIndex.value, index)
    isDragging.value = false
    dragStartIndex.value = null
    dragCurrentIndex.value = null
    hasDragged.value = false
  }
}

// 鼠标/触摸松开
function handleMouseUp(index: number) {
  if (!isDragging.value) return
  
  const dragDuration = Date.now() - dragStartTime.value
  isDragging.value = false
  
  // 如果没有拖拽（短时间点击），执行点击逻辑
  if (!hasDragged.value && dragDuration < DRAG_THRESHOLD) {
    handleCellClick(index)
  }
  
  dragStartIndex.value = null
  dragCurrentIndex.value = null
  hasDragged.value = false
}

function handleTouchEnd(index: number) {
  handleMouseUp(index)
}

// 处理触摸移动（用于滑动交换）
function handleTouchMove(event: TouchEvent, currentIndex: number) {
  if (!isDragging.value || dragStartIndex.value === null) return
  
  event.preventDefault()
  hasDragged.value = true
  
  // 获取触摸位置
  const touch = event.touches[0]
  const boardElement = document.querySelector('.game-board')
  if (!boardElement) return
  
  const rect = boardElement.getBoundingClientRect()
  const cellWidth = rect.width / BOARD_SIZE
  const cellHeight = rect.height / BOARD_SIZE
  
  // 计算当前触摸位置对应的格子
  const col = Math.floor((touch.clientX - rect.left) / cellWidth)
  const row = Math.floor((touch.clientY - rect.top) / cellHeight)
  
  if (row >= 0 && row < BOARD_SIZE && col >= 0 && col < BOARD_SIZE) {
    const targetIndex = row * BOARD_SIZE + col
    
    if (targetIndex !== dragCurrentIndex.value) {
      dragCurrentIndex.value = targetIndex
      
      // 检查是否滑动到相邻格子
      const startRow = Math.floor(dragStartIndex.value / BOARD_SIZE)
      const startCol = dragStartIndex.value % BOARD_SIZE
      
      const isAdjacent = (Math.abs(startRow - row) === 1 && startCol === col) ||
                         (Math.abs(startCol - col) === 1 && startRow === row)
      
      if (isAdjacent && dragStartIndex.value !== targetIndex) {
        trySwap(dragStartIndex.value, targetIndex)
        isDragging.value = false
        dragStartIndex.value = null
        dragCurrentIndex.value = null
        hasDragged.value = false
      }
    }
  }
}

// 尝试交换
async function trySwap(index1: number, index2: number) {
  isProcessing.value = true
  selectedIndex.value = null
  
  const row1 = Math.floor(index1 / BOARD_SIZE)
  const col1 = index1 % BOARD_SIZE
  const row2 = Math.floor(index2 / BOARD_SIZE)
  const col2 = index2 % BOARD_SIZE
  
  const cell1 = board.value[row1][col1]
  const cell2 = board.value[row2][col2]
  
  // 检查是否是两个特殊道具交换
  if (cell1.special && cell2.special) {
    await activateSpecialCombo(index1, index2)
    return
  }
  
  // 检查是否是一个道具和普通方块交换
  if (cell1.special || cell2.special) {
    const specialIndex = cell1.special ? index1 : index2
    const normalIndex = cell1.special ? index2 : index1
    await activateSpecial(specialIndex, normalIndex)
    return
  }
  
  // 显示交换动画
  swappingIndices.value = { from: index1, to: index2 }
  await delay(200)
  
  // 执行交换
  const temp = { ...cell1 }
  board.value[row1][col1] = { ...cell2 }
  board.value[row2][col2] = temp
  
  // 清除交换动画
  swappingIndices.value = null
  
  const { matches } = findMatches()
  
  if (matches.size > 0) {
    await processMatches()
  } else {
    // 交换失败，显示回退动画
    swappingIndices.value = { from: index2, to: index1 }
    await delay(200)
    board.value[row2][col2] = board.value[row1][col1]
    board.value[row1][col1] = temp
    swappingIndices.value = null
    isProcessing.value = false
  }
}

// 激活特殊道具
async function activateSpecial(specialIndex: number, targetIndex: number) {
  const row = Math.floor(specialIndex / BOARD_SIZE)
  const col = specialIndex % BOARD_SIZE
  const special = board.value[row][col].special
  
  if (!special) {
    isProcessing.value = false
    return
  }
  
  combo.value++
  const targetRow = Math.floor(targetIndex / BOARD_SIZE)
  const targetCol = targetIndex % BOARD_SIZE
  const targetType = board.value[targetRow][targetCol].type
  
  const toClear = new Set<number>()
  
  switch (special) {
    case SPECIAL.ROCKET_H:
      // 消除整行
      for (let c = 0; c < BOARD_SIZE; c++) {
        toClear.add(row * BOARD_SIZE + c)
      }
      break
    case SPECIAL.ROCKET_V:
      // 消除整列
      for (let r = 0; r < BOARD_SIZE; r++) {
        toClear.add(r * BOARD_SIZE + col)
      }
      break
    case SPECIAL.BOMB:
      // 消除周围3x3
      for (let r = Math.max(0, row - 1); r <= Math.min(BOARD_SIZE - 1, row + 1); r++) {
        for (let c = Math.max(0, col - 1); c <= Math.min(BOARD_SIZE - 1, col + 1); c++) {
          toClear.add(r * BOARD_SIZE + c)
        }
      }
      break
    case SPECIAL.RAINBOW:
      // 消除全屏同色（包括彩虹球自身）
      toClear.add(specialIndex) // 彩虹球自身也要被消除
      for (let r = 0; r < BOARD_SIZE; r++) {
        for (let c = 0; c < BOARD_SIZE; c++) {
          if (board.value[r][c].type === targetType) {
            toClear.add(r * BOARD_SIZE + c)
          }
        }
      }
      break
  }
  
  // 显示特效
  matchedIndices.value = toClear
  await delay(300)
  
  // 计算分数
  score.value += toClear.size * 15 + comboBonus.value
  
  // 清除
  toClear.forEach(index => {
    const r = Math.floor(index / BOARD_SIZE)
    const c = index % BOARD_SIZE
    board.value[r][c] = { type: -1, special: null }
  })
  
  matchedIndices.value.clear()
  await delay(200)
  
  // 下落和填充
  await dropCells()
  fillNewCells()
  await delay(200)
  
  // 检查连锁
  await checkChainReaction()
}

// 激活两个特殊道具的组合
async function activateSpecialCombo(index1: number, index2: number) {
  const row1 = Math.floor(index1 / BOARD_SIZE)
  const col1 = index1 % BOARD_SIZE
  const row2 = Math.floor(index2 / BOARD_SIZE)
  const col2 = index2 % BOARD_SIZE
  
  const special1 = board.value[row1][col1].special
  const special2 = board.value[row2][col2].special
  
  combo.value += 2
  
  const toClear = new Set<number>()
  
  // 火箭+火箭 = 十字消除
  if ((special1 === SPECIAL.ROCKET_H || special1 === SPECIAL.ROCKET_V) &&
      (special2 === SPECIAL.ROCKET_H || special2 === SPECIAL.ROCKET_V)) {
    for (let c = 0; c < BOARD_SIZE; c++) {
      toClear.add(row1 * BOARD_SIZE + c)
    }
    for (let r = 0; r < BOARD_SIZE; r++) {
      toClear.add(r * BOARD_SIZE + col1)
    }
  }
  // 炸弹+炸弹 = 超大范围
  else if (special1 === SPECIAL.BOMB && special2 === SPECIAL.BOMB) {
    for (let r = Math.max(0, row1 - 2); r <= Math.min(BOARD_SIZE - 1, row1 + 2); r++) {
      for (let c = Math.max(0, col1 - 2); c <= Math.min(BOARD_SIZE - 1, col1 + 2); c++) {
        toClear.add(r * BOARD_SIZE + c)
      }
    }
  }
  // 彩虹球+任意 = 全屏消除该类型
  else if (special1 === SPECIAL.RAINBOW || special2 === SPECIAL.RAINBOW) {
    const rainbowIndex = special1 === SPECIAL.RAINBOW ? index1 : index2
    const otherIndex = special1 === SPECIAL.RAINBOW ? index2 : index1
    const otherRow = Math.floor(otherIndex / BOARD_SIZE)
    const otherCol = otherIndex % BOARD_SIZE
    const targetType = board.value[otherRow][otherCol].type
    
    for (let r = 0; r < BOARD_SIZE; r++) {
      for (let c = 0; c < BOARD_SIZE; c++) {
        if (board.value[r][c].type === targetType || board.value[r][c].special) {
          toClear.add(r * BOARD_SIZE + c)
        }
      }
    }
  }
  // 其他组合 = 各自效果叠加
  else {
    // 先触发第一个
    await activateSpecial(index1, index2)
    // 再触发第二个
    await activateSpecial(index2, index1)
    return
  }
  
  // 显示特效
  matchedIndices.value = toClear
  await delay(300)
  
  // 计算分数
  score.value += toClear.size * 20 + comboBonus.value
  
  // 清除
  toClear.forEach(index => {
    const r = Math.floor(index / BOARD_SIZE)
    const c = index % BOARD_SIZE
    board.value[r][c] = { type: -1, special: null }
  })
  
  matchedIndices.value.clear()
  await delay(200)
  
  // 下落和填充
  await dropCells()
  fillNewCells()
  await delay(200)
  
  // 检查连锁
  await checkChainReaction()
}

// 处理匹配
async function processMatches() {
  const { matches, specialCells } = findMatches()
  
  if (matches.size === 0) {
    combo.value = 0
    isProcessing.value = false
    
    if (!hasPossibleMoves()) {
      gameOver.value = true
      saveHighScore()
    }
    return
  }
  
  combo.value++
  
  // 显示匹配动画
  matchedIndices.value = matches
  await delay(300)
  
  // 计算分数
  const baseScore = matches.size * 10
  const bonus = comboBonus.value
  score.value += baseScore + bonus
  
  // 保存特殊道具的类型和位置
  const specialToCreate: { row: number, col: number, type: number, special: string }[] = []
  specialCells.forEach((special, index) => {
    const row = Math.floor(index / BOARD_SIZE)
    const col = index % BOARD_SIZE
    const type = board.value[row][col].type
    specialToCreate.push({ row, col, type, special })
  })
  
  // 清除匹配的格子
  matches.forEach(index => {
    const row = Math.floor(index / BOARD_SIZE)
    const col = index % BOARD_SIZE
    board.value[row][col] = { type: -1, special: null }
  })
  
  matchedIndices.value.clear()
  await delay(200)
  
  // 下落
  await dropCells()
  
  // 填充新元素
  fillNewCells()
  await delay(200)
  
  // 创建特殊道具
  specialToCreate.forEach(({ row, col, type, special }) => {
    board.value[row][col] = { type, special }
  })
  
  // 检查连锁反应
  await processMatches()
}

// 检查连锁反应
async function checkChainReaction() {
  const { matches } = findMatches()
  if (matches.size > 0) {
    await processMatches()
  } else {
    combo.value = 0
    isProcessing.value = false
    
    if (!hasPossibleMoves()) {
      gameOver.value = true
      saveHighScore()
    }
  }
}

// 下落
async function dropCells() {
  fallingIndices.value.clear()
  
  for (let col = 0; col < BOARD_SIZE; col++) {
    let emptyRow = BOARD_SIZE - 1
    
    for (let row = BOARD_SIZE - 1; row >= 0; row--) {
      if (board.value[row][col].type !== -1) {
        if (row !== emptyRow) {
          board.value[emptyRow][col] = { ...board.value[row][col] }
          board.value[row][col] = { type: -1, special: null }
          fallingIndices.value.add(emptyRow * BOARD_SIZE + col)
        }
        emptyRow--
      }
    }
  }
  
  await delay(200)
  fallingIndices.value.clear()
}

// 填充新元素
function fillNewCells() {
  for (let row = 0; row < BOARD_SIZE; row++) {
    for (let col = 0; col < BOARD_SIZE; col++) {
      if (board.value[row][col].type === -1) {
        board.value[row][col] = {
          type: Math.floor(Math.random() * CELL_TYPES),
          special: null
        }
      }
    }
  }
}

// 检查是否有可移动
function hasPossibleMoves(): boolean {
  for (let row = 0; row < BOARD_SIZE; row++) {
    for (let col = 0; col < BOARD_SIZE; col++) {
      // 尝试右交换
      if (col < BOARD_SIZE - 1) {
        swapTemp(row, col, row, col + 1)
        const hasMatch = findMatches().matches.size > 0
        swapTemp(row, col, row, col + 1)
        if (hasMatch) return true
      }
      
      // 尝试下交换
      if (row < BOARD_SIZE - 1) {
        swapTemp(row, col, row + 1, col)
        const hasMatch = findMatches().matches.size > 0
        swapTemp(row, col, row + 1, col)
        if (hasMatch) return true
      }
    }
  }
  return false
}

// 临时交换
function swapTemp(row1: number, col1: number, row2: number, col2: number) {
  const temp = { ...board.value[row1][col1] }
  board.value[row1][col1] = { ...board.value[row2][col2] }
  board.value[row2][col2] = temp
}

// 获取单元格样式
function getCellStyle(index: number) {
  const row = Math.floor(index / BOARD_SIZE)
  const col = index % BOARD_SIZE
  return {
    gridRow: row + 1,
    gridColumn: col + 1
  }
}

// 获取特效图标
function getSpecialIcon(special: string): string {
  const icons: Record<string, string> = {
    'bomb': '💣',
    'rocket_h': '➡️',
    'rocket_v': '⬇️',
    'rainbow': '🌈'
  }
  return icons[special] || ''
}

// 延迟
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// 保存最高分
function saveHighScore() {
  if (score.value > highScore.value) {
    highScore.value = score.value
    localStorage.setItem('match3_highscore', score.value.toString())
  }
  const games = parseInt(localStorage.getItem('match3_games') || '0')
  localStorage.setItem('match3_games', (games + 1).toString())
}

// 返回
function goBack() {
  router.push('/game/match3')
}

// 重新开始
function restartGame() {
  initGame()
}

onMounted(() => {
  highScore.value = parseInt(localStorage.getItem('match3_highscore') || '0')
  initGame()
})
</script>

<style scoped>
.match3-game {
  min-height: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.top-bar {
  width: 100%;
  max-width: 400px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.back-btn {
  padding: 8px 20px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.back-btn:hover {
  border-color: #ff00ff;
  color: #ff00ff;
}

.score-info {
  display: flex;
  gap: 20px;
}

.score-item {
  text-align: center;
}

.score-item .label {
  display: block;
  color: #888;
  font-size: 0.8em;
}

.score-item .value {
  display: block;
  color: #fff;
  font-size: 1.5em;
  font-weight: bold;
}

/* 连击提示 - 绝对定位覆盖层 */
.combo-overlay {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 50;
  pointer-events: none;
}

.combo-display {
  text-align: center;
  padding: 20px 40px;
  background: rgba(0, 0, 0, 0.8);
  border-radius: 20px;
  border: 2px solid #ff00ff;
  box-shadow: 0 0 30px rgba(255, 0, 255, 0.5), inset 0 0 20px rgba(255, 0, 255, 0.1);
  animation: comboPopup 0.5s ease-out;
}

@keyframes comboPopup {
  0% { transform: scale(0.5); opacity: 0; }
  50% { transform: scale(1.1); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}

.combo-text {
  display: block;
  font-size: 2em;
  font-weight: bold;
  color: #ff00ff;
  text-shadow: 0 0 20px #ff00ff, 0 0 40px #ff00ff;
  animation: pulse 0.5s ease-in-out infinite alternate;
}

.bonus {
  display: block;
  color: #00f5ff;
  font-size: 1.5em;
  margin-top: 5px;
  text-shadow: 0 0 10px #00f5ff;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

.game-board {
  display: grid;
  grid-template-columns: repeat(8, 45px);
  grid-template-rows: repeat(8, 45px);
  gap: 4px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.cell {
  width: 45px;
  height: 45px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.cell:hover {
  transform: scale(1.05);
}

.cell.is-selected {
  box-shadow: 0 0 15px #fff;
  transform: scale(1.1);
  z-index: 10;
}

.cell.is-matched {
  animation: matchAnim 0.3s ease-out;
}

.cell.is-falling {
  animation: fallAnim 0.2s ease-in;
}

.cell.is-bomb {
  box-shadow: 0 0 15px #ff4444, inset 0 0 10px rgba(255, 68, 68, 0.5);
  animation: bombPulse 0.8s ease-in-out infinite;
}

.cell.is-rocket-h,
.cell.is-rocket-v {
  box-shadow: 0 0 15px #44ff44, inset 0 0 10px rgba(68, 255, 68, 0.5);
  animation: rocketGlow 1s ease-in-out infinite;
}

.cell.is-rainbow {
  box-shadow: 0 0 15px #ff00ff, inset 0 0 10px rgba(255, 0, 255, 0.5);
  animation: rainbowGlow 1.5s linear infinite;
}

/* 交换动画 */
.cell.is-swapping {
  animation: swapAnim 0.2s ease-in-out;
  z-index: 20;
}

@keyframes swapAnim {
  0% { transform: scale(1); }
  50% { transform: scale(0.8); }
  100% { transform: scale(1); }
}

@keyframes matchAnim {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.5; }
  100% { transform: scale(0); opacity: 0; }
}

@keyframes fallAnim {
  0% { transform: translateY(-20px); }
  100% { transform: translateY(0); }
}

@keyframes bombPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

@keyframes rocketGlow {
  0%, 100% { box-shadow: 0 0 15px #44ff44, inset 0 0 10px rgba(68, 255, 68, 0.5); }
  50% { box-shadow: 0 0 25px #44ff44, inset 0 0 15px rgba(68, 255, 68, 0.7); }
}

@keyframes rainbowGlow {
  0% { filter: hue-rotate(0deg); }
  100% { filter: hue-rotate(360deg); }
}

/* 颜色 - 带可爱emoji图标 */
.color-0 { 
  background: linear-gradient(135deg, #ff6b8a, #ff8fa3);
  box-shadow: inset 0 0 10px rgba(255,255,255,0.3), 0 2px 5px rgba(255,107,138,0.4);
}
.color-0::before {
  content: "🍓";
  font-size: 1.8em;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.2));
}
.color-1 { 
  background: linear-gradient(135deg, #7ee787, #4ade80);
  box-shadow: inset 0 0 10px rgba(255,255,255,0.3), 0 2px 5px rgba(126,231,135,0.4);
}
.color-1::before {
  content: "🍀";
  font-size: 1.8em;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.2));
}
.color-2 { 
  background: linear-gradient(135deg, #67e8f9, #22d3ee);
  box-shadow: inset 0 0 10px rgba(255,255,255,0.3), 0 2px 5px rgba(103,232,249,0.4);
}
.color-2::before {
  content: "💧";
  font-size: 1.8em;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.2));
}
.color-3 { 
  background: linear-gradient(135deg, #fde047, #facc15);
  box-shadow: inset 0 0 10px rgba(255,255,255,0.3), 0 2px 5px rgba(253,224,71,0.4);
}
.color-3::before {
  content: "⭐";
  font-size: 1.8em;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.2));
}
.color-4 { 
  background: linear-gradient(135deg, #c084fc, #a855f7);
  box-shadow: inset 0 0 10px rgba(255,255,255,0.3), 0 2px 5px rgba(192,132,252,0.4);
}
.color-4::before {
  content: "💎";
  font-size: 1.8em;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.2));
}
.color-5 { 
  background: linear-gradient(135deg, #fb923c, #f97316);
  box-shadow: inset 0 0 10px rgba(255,255,255,0.3), 0 2px 5px rgba(251,146,60,0.4);
}
.color-5::before {
  content: "🥕";
  font-size: 1.8em;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.2));
}

.special-icon {
  font-size: 1.2em;
  position: absolute;
  top: 2px;
  right: 2px;
  z-index: 5;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.overlay h2 {
  color: #fff;
  font-size: 2em;
  margin-bottom: 20px;
}

.final-score {
  color: #00f5ff;
  font-size: 1.5em;
  margin-bottom: 10px;
}

.new-record {
  color: #ff00ff;
  font-size: 1.2em;
  margin-bottom: 20px;
}

.restart-btn {
  padding: 15px 40px;
  background: linear-gradient(45deg, #ff0066, #ff00ff);
  border: none;
  color: #fff;
  border-radius: 30px;
  font-size: 1.2em;
  cursor: pointer;
  transition: all 0.3s;
}

.restart-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 0 30px rgba(255, 0, 255, 0.5);
}

.tip {
  margin-top: 10px;
  color: #888;
  font-size: 0.85em;
  text-align: center;
}

@media (max-width: 768px) {
  .game-board {
    grid-template-columns: repeat(8, 40px);
    grid-template-rows: repeat(8, 40px);
    gap: 3px;
  }
  
  .cell {
    width: 40px;
    height: 40px;
  }
  
  .color-0::before,
  .color-1::before,
  .color-2::before,
  .color-3::before,
  .color-4::before,
  .color-5::before {
    font-size: 1.5em;
  }
}
</style>
