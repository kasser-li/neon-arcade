<template>
  <div class="match3-level">
    <!-- 顶部信息栏 -->
    <div class="top-bar">
      <button class="back-btn" @click="goBack">← 返回</button>
      <div class="level-info">
        <span class="level-name">第 {{ currentLevel.id }} 关</span>
        <span class="level-title">{{ currentLevel.name }}</span>
      </div>
    </div>
    
    <!-- 金币显示 -->
    <div class="coins-display">
      <span class="coin-icon">💰</span>
      <span class="coin-value">{{ coins }}</span>
      <span v-if="earnedCoins > 0" class="earned">+{{ earnedCoins }}</span>
    </div>

    <!-- 任务目标面板 -->
    <div class="objectives-panel">
      <div class="objective" v-for="(obj, index) in currentLevel.objectives" :key="index"
           :class="{ 'completed': isObjectiveCompleted(obj) }">
        <span class="obj-icon">{{ getObjectiveIcon(obj) }}</span>
        <span class="obj-text">{{ getObjectiveText(obj) }}</span>
        <span class="obj-progress">{{ getObjectiveProgress(obj) }}</span>
      </div>
      <div class="moves-left">
        <span class="moves-label">剩余步数</span>
        <span class="moves-value" :class="{ 'warning': movesLeft <= 5, 'danger': movesLeft <= 3 }">
          {{ movesLeft }}
        </span>
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
        :disabled="shopStore.getPowerUpCount(powerUp.id) <= 0 || isProcessing || levelComplete || levelFailed"
      >
        <span class="powerup-icon">{{ powerUp.icon }}</span>
        <span class="powerup-count">{{ shopStore.getPowerUpCount(powerUp.id) }}</span>
      </button>
    </div>
    
    <!-- 连击显示 -->
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
            'is-swapping': swappingIndices && (swappingIndices.from === index || swappingIndices.to === index),
            'is-obstacle': cell.isObstacle
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
        <span v-if="cell.isObstacle" class="obstacle-icon">🧊</span>
      </div>
    </div>
    
    <!-- 关卡完成弹窗 -->
    <div v-if="levelComplete" class="overlay">
      <div class="result-card success">
        <h2>🎉 关卡完成！</h2>
        <div class="stars">
          <span v-for="i in 3" :key="i" class="star" :class="{ 'earned': i <= earnedStars }">⭐</span>
        </div>
        <p class="result-score">得分: {{ score }}</p>
        <p class="result-moves">剩余步数: {{ movesLeft }}</p>
        <div class="result-buttons">
          <button class="btn-primary" @click="nextLevel">下一关</button>
          <button class="btn-secondary" @click="restartLevel">重玩本关</button>
        </div>
      </div>
    </div>
    
    <!-- 关卡失败弹窗 -->
    <div v-if="levelFailed" class="overlay">
      <div class="result-card failure">
        <h2>💔 关卡失败</h2>
        <p class="fail-reason">{{ failReason }}</p>
        <div class="result-buttons">
          <button class="btn-primary" @click="restartLevel">再试一次</button>
          <button class="btn-secondary" @click="goBack">返回关卡选择</button>
        </div>
      </div>
    </div>
    
    <!-- 提示 -->
    <p class="tip">点击两个相邻元素交换位置</p>
    <p class="tip">4连消=火箭 🚀 | 5连消=炸弹 💣 | T/L型=彩虹球 🌈</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { LEVELS, saveLevelProgress, TOTAL_LEVELS, type LevelObjective } from './match3Levels'
import { useMatch3ShopStore, POWER_UPS, type PowerUpType } from '../stores/match3Shop'

const router = useRouter()
const route = useRoute()
const shopStore = useMatch3ShopStore()

// 道具系统
const coins = ref(0)
const earnedCoins = ref(0)
const activePowerUp = ref<PowerUpType | null>(null)
const availablePowerUps = computed(() => POWER_UPS.filter(p => p.type === 'ingame'))

// 游戏配置
const BOARD_SIZE = 8
const CELL_TYPES = 6

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
  isObstacle?: boolean
  obstacleType?: string
}

// 游戏状态
const board = ref<Cell[][]>([])
const selectedIndex = ref<number | null>(null)
const score = ref(0)
const movesLeft = ref(0)
const combo = ref(0)
const levelComplete = ref(false)
const levelFailed = ref(false)
const failReason = ref('')
const isProcessing = ref(false)
const matchedIndices = ref<Set<number>>(new Set())
const fallingIndices = ref<Set<number>>(new Set())
const swappingIndices = ref<{ from: number; to: number } | null>(null)

// 关卡进度追踪
const objectiveProgress = ref<Record<string, number>>({})
const specialUsed = ref(0)
const maxCombo = ref(0)

// 当前关卡
const currentLevel = computed(() => {
  const levelId = parseInt(route.params.id as string) || 1
  return LEVELS.find(l => l.id === levelId) || LEVELS[0]
})

// 计算星星数
const earnedStars = computed(() => {
  const level = currentLevel.value
  if (score.value >= level.starRequirements[2]) return 3
  if (score.value >= level.starRequirements[1]) return 2
  if (score.value >= level.starRequirements[0]) return 1
  return 0
})

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
const comboBonus = computed(() => combo.value * 10)

// 初始化关卡
function initLevel() {
  const level = currentLevel.value
  
  // 加载商店数据
  shopStore.loadData()
  coins.value = shopStore.coins
  earnedCoins.value = 0
  activePowerUp.value = null
  
  if (level.customBoard) {
    board.value = level.customBoard.map(row => 
      row.map(cell => ({
        type: cell.type,
        special: cell.special || null,
        isObstacle: cell.isObstacle,
        obstacleType: cell.obstacleType
      }))
    )
  } else {
    board.value = generateBoard(level.blockedCells || [])
  }
  
  // 应用开局道具
  if (shopStore.selectedPrePowerUp === 'rainbow_start') {
    const randomRow = Math.floor(Math.random() * BOARD_SIZE)
    const randomCol = Math.floor(Math.random() * BOARD_SIZE)
    if (!board.value[randomRow][randomCol].isObstacle) {
      board.value[randomRow][randomCol].special = SPECIAL.RAINBOW
    }
    shopStore.usePowerUp('rainbow_start')
  }
  
  score.value = 0
  movesLeft.value = level.moves
  combo.value = 0
  levelComplete.value = false
  levelFailed.value = false
  selectedIndex.value = null
  matchedIndices.value.clear()
  fallingIndices.value.clear()
  specialUsed.value = 0
  maxCombo.value = 0
  
  objectiveProgress.value = {}
  level.objectives.forEach(obj => {
    objectiveProgress.value[obj.type] = 0
  })
  
  while (hasMatches().size > 0) {
    if (level.customBoard) break
    board.value = generateBoard(level.blockedCells || [])
  }
}

function generateBoard(blockedCells: {row: number, col: number}[]): Cell[][] {
  const newBoard: Cell[][] = []
  for (let row = 0; row < BOARD_SIZE; row++) {
    newBoard[row] = []
    for (let col = 0; col < BOARD_SIZE; col++) {
      const isBlocked = blockedCells.some(b => b.row === row && b.col === col)
      if (isBlocked) {
        newBoard[row][col] = { type: -1, special: null, isObstacle: true, obstacleType: 'rock' }
      } else {
        newBoard[row][col] = { type: Math.floor(Math.random() * CELL_TYPES), special: null }
      }
    }
  }
  return newBoard
}

function hasMatches(): Set<number> {
  return findMatches().matches
}

function findMatches(): { matches: Set<number>, specialCells: Map<number, string> } {
  const matches = new Set<number>()
  const specialCells = new Map<number, string>()
  
  for (let row = 0; row < BOARD_SIZE; row++) {
    let count = 1, startCol = 0
    for (let col = 1; col <= BOARD_SIZE; col++) {
      if (col < BOARD_SIZE && board.value[row][col].type === board.value[row][col-1].type && board.value[row][col].type !== -1) {
        count++
      } else {
        if (count >= 3) {
          for (let i = startCol; i < startCol + count; i++) matches.add(row * BOARD_SIZE + i)
          const center = row * BOARD_SIZE + Math.floor(startCol + count / 2)
          if (count === 4) specialCells.set(center, SPECIAL.ROCKET_H)
          else if (count >= 5) specialCells.set(center, SPECIAL.BOMB)
        }
        count = 1
        startCol = col
      }
    }
  }
  
  for (let col = 0; col < BOARD_SIZE; col++) {
    let count = 1, startRow = 0
    for (let row = 1; row <= BOARD_SIZE; row++) {
      if (row < BOARD_SIZE && board.value[row][col].type === board.value[row-1][col].type && board.value[row][col].type !== -1) {
        count++
      } else {
        if (count >= 3) {
          for (let i = startRow; i < startRow + count; i++) matches.add(i * BOARD_SIZE + col)
          const center = Math.floor(startRow + count / 2) * BOARD_SIZE + col
          if (count === 4) {
            if (specialCells.has(center) && specialCells.get(center) === SPECIAL.ROCKET_H) {
              specialCells.set(center, SPECIAL.BOMB)
            } else {
              specialCells.set(center, SPECIAL.ROCKET_V)
            }
          } else if (count >= 5) specialCells.set(center, SPECIAL.BOMB)
        }
        count = 1
        startRow = row
      }
    }
  }
  
  checkTLShape(matches, specialCells)
  return { matches, specialCells }
}

function checkTLShape(matches: Set<number>, specialCells: Map<number, string>) {
  for (let row = 0; row < BOARD_SIZE - 2; row++) {
    for (let col = 0; col < BOARD_SIZE - 2; col++) {
      const type = board.value[row][col].type
      if (type === -1) continue
      
      if (col + 2 < BOARD_SIZE && row + 2 < BOARD_SIZE) {
        if (board.value[row][col+1].type === type && board.value[row][col+2].type === type &&
            board.value[row+1][col+1].type === type && board.value[row+2][col+1].type === type) {
          const center = row * BOARD_SIZE + col + 1
          if (!specialCells.has(center)) specialCells.set(center, SPECIAL.RAINBOW)
        }
      }
      
      if (col + 2 < BOARD_SIZE && row >= 2) {
        if (board.value[row][col+1].type === type && board.value[row][col+2].type === type &&
            board.value[row-1][col+1].type === type && board.value[row-2][col+1].type === type) {
          const center = row * BOARD_SIZE + col + 1
          if (!specialCells.has(center)) specialCells.set(center, SPECIAL.RAINBOW)
        }
      }
      
      if (col + 2 < BOARD_SIZE && row + 2 < BOARD_SIZE) {
        if (board.value[row+1][col].type === type && board.value[row+2][col].type === type &&
            board.value[row+2][col+1].type === type && board.value[row+2][col+2].type === type) {
          const center = (row + 2) * BOARD_SIZE + col
          if (!specialCells.has(center)) specialCells.set(center, SPECIAL.RAINBOW)
        }
      }
    }
  }
}

// 目标相关函数
function isObjectiveCompleted(obj: LevelObjective): boolean {
  switch (obj.type) {
    case 'score': return score.value >= obj.target
    case 'collect': return (objectiveProgress.value['collect_' + obj.targetType] || 0) >= obj.target
    case 'clear_obstacle': return (objectiveProgress.value['clear_obstacle'] || 0) >= obj.target
    case 'combo': return maxCombo.value >= obj.target
    case 'special': return specialUsed.value >= obj.target
    default: return false
  }
}

function getObjectiveIcon(obj: LevelObjective): string {
  const icons: Record<string, string> = {
    'score': '🎯',
    'collect': '📦',
    'clear_obstacle': '🔨',
    'combo': '⚡',
    'special': '💎'
  }
  return icons[obj.type] || '📋'
}

function getObjectiveText(obj: LevelObjective): string {
  if (obj.description) return obj.description
  switch (obj.type) {
    case 'score': return `达到 ${obj.target} 分`
    case 'collect': return `收集 ${obj.target} 个元素`
    case 'clear_obstacle': return `清除 ${obj.target} 个障碍`
    case 'combo': return `达成 ${obj.target} 连击`
    case 'special': return `使用 ${obj.target} 个道具`
    default: return ''
  }
}

function getObjectiveProgress(obj: LevelObjective): string {
  let current = 0
  switch (obj.type) {
    case 'score': current = score.value; break
    case 'collect': current = objectiveProgress.value['collect_' + obj.targetType] || 0; break
    case 'clear_obstacle': current = objectiveProgress.value['clear_obstacle'] || 0; break
    case 'combo': current = maxCombo.value; break
    case 'special': current = specialUsed.value; break
  }
  return `${current}/${obj.target}`
}

function checkAllObjectives(): boolean {
  return currentLevel.value.objectives.every(obj => isObjectiveCompleted(obj))
}

// 输入处理
const isDragging = ref(false)
const dragStartIndex = ref<number | null>(null)
const dragStartTime = ref(0)
const hasDragged = ref(false)

function handleMouseDown(index: number) {
  if (isProcessing.value || levelComplete.value || levelFailed.value) return
  if (board.value[Math.floor(index / BOARD_SIZE)][index % BOARD_SIZE].isObstacle) return
  isDragging.value = true
  hasDragged.value = false
  dragStartIndex.value = index
  dragStartTime.value = Date.now()
}

function handleTouchStart(index: number) {
  handleMouseDown(index)
}

function handleMouseEnter(index: number) {
  if (!isDragging.value || dragStartIndex.value === null) return
  hasDragged.value = true
  const row1 = Math.floor(dragStartIndex.value / BOARD_SIZE)
  const col1 = dragStartIndex.value % BOARD_SIZE
  const row2 = Math.floor(index / BOARD_SIZE)
  const col2 = index % BOARD_SIZE
  const isAdjacent = (Math.abs(row1 - row2) === 1 && col1 === col2) || (Math.abs(col1 - col2) === 1 && row1 === row2)
  if (isAdjacent && dragStartIndex.value !== index) {
    trySwap(dragStartIndex.value, index)
    isDragging.value = false
    dragStartIndex.value = null
    hasDragged.value = false
  }
}

function handleMouseUp(index: number) {
  if (!isDragging.value) return
  const duration = Date.now() - dragStartTime.value
  isDragging.value = false
  if (!hasDragged.value && duration < 200) {
    handleCellClick(index)
  }
  dragStartIndex.value = null
  hasDragged.value = false
}

function handleTouchEnd(index: number) {
  handleMouseUp(index)
}

function handleTouchMove(event: TouchEvent, currentIndex: number) {
  if (!isDragging.value || dragStartIndex.value === null) return
  event.preventDefault()
  hasDragged.value = true
}

function handleCellClick(index: number) {
  if (isProcessing.value || levelComplete.value || levelFailed.value) return
  const cell = board.value[Math.floor(index / BOARD_SIZE)][index % BOARD_SIZE]
  if (cell.isObstacle) return
  
  if (selectedIndex.value === null) {
    selectedIndex.value = index
  } else if (selectedIndex.value === index) {
    selectedIndex.value = null
  } else {
    const row1 = Math.floor(selectedIndex.value / BOARD_SIZE)
    const col1 = selectedIndex.value % BOARD_SIZE
    const row2 = Math.floor(index / BOARD_SIZE)
    const col2 = index % BOARD_SIZE
    const isAdjacent = (Math.abs(row1 - row2) === 1 && col1 === col2) || (Math.abs(col1 - col2) === 1 && row1 === row2)
    if (isAdjacent) {
      trySwap(selectedIndex.value, index)
    } else {
      selectedIndex.value = index
    }
  }
}

// 交换逻辑
async function trySwap(index1: number, index2: number) {
  isProcessing.value = true
  selectedIndex.value = null
  
  const row1 = Math.floor(index1 / BOARD_SIZE)
  const col1 = index1 % BOARD_SIZE
  const row2 = Math.floor(index2 / BOARD_SIZE)
  const col2 = index2 % BOARD_SIZE
  
  const cell1 = board.value[row1][col1]
  const cell2 = board.value[row2][col2]
  
  if (cell1.isObstacle || cell2.isObstacle) {
    isProcessing.value = false
    return
  }
  
  if (cell1.special && cell2.special) {
    specialUsed.value += 2
    await activateSpecialCombo(index1, index2)
    movesLeft.value--
    checkEndConditions()
    return
  }
  
  if (cell1.special || cell2.special) {
    specialUsed.value++
    const specialIndex = cell1.special ? index1 : index2
    const normalIndex = cell1.special ? index2 : index1
    await activateSpecial(specialIndex, normalIndex)
    movesLeft.value--
    checkEndConditions()
    return
  }
  
  swappingIndices.value = { from: index1, to: index2 }
  await delay(200)
  
  const temp = { ...cell1 }
  board.value[row1][col1] = { ...cell2 }
  board.value[row2][col2] = temp
  
  swappingIndices.value = null
  
  const { matches } = findMatches()
  
  if (matches.size > 0) {
    movesLeft.value--
    await processMatches()
    checkEndConditions()
  } else {
    swappingIndices.value = { from: index2, to: index1 }
    await delay(200)
    board.value[row2][col2] = board.value[row1][col1]
    board.value[row1][col1] = temp
    swappingIndices.value = null
    isProcessing.value = false
  }
}

async function activateSpecial(specialIndex: number, targetIndex: number) {
  const row = Math.floor(specialIndex / BOARD_SIZE)
  const col = specialIndex % BOARD_SIZE
  const special = board.value[row][col].special
  
  if (!special) {
    isProcessing.value = false
    return
  }
  
  combo.value++
  maxCombo.value = Math.max(maxCombo.value, combo.value)
  const targetRow = Math.floor(targetIndex / BOARD_SIZE)
  const targetCol = targetIndex % BOARD_SIZE
  const targetType = board.value[targetRow][targetCol].type
  
  const toClear = new Set<number>()
  
  switch (special) {
    case SPECIAL.ROCKET_H:
      for (let c = 0; c < BOARD_SIZE; c++) toClear.add(row * BOARD_SIZE + c)
      break
    case SPECIAL.ROCKET_V:
      for (let r = 0; r < BOARD_SIZE; r++) toClear.add(r * BOARD_SIZE + col)
      break
    case SPECIAL.BOMB:
      for (let r = Math.max(0, row - 1); r <= Math.min(BOARD_SIZE - 1, row + 1); r++) {
        for (let c = Math.max(0, col - 1); c <= Math.min(BOARD_SIZE - 1, col + 1); c++) {
          toClear.add(r * BOARD_SIZE + c)
        }
      }
      break
    case SPECIAL.RAINBOW:
      toClear.add(specialIndex)
      for (let r = 0; r < BOARD_SIZE; r++) {
        for (let c = 0; c < BOARD_SIZE; c++) {
          if (board.value[r][c].type === targetType) {
            toClear.add(r * BOARD_SIZE + c)
          }
        }
      }
      break
  }
  
  matchedIndices.value = toClear
  await delay(300)
  
  updateObjectives(toClear)
  score.value += toClear.size * 15 + comboBonus.value
  
  // 金币奖励
  earnedCoins.value += toClear.size
  earnedCoins.value += combo.value * 5
  
  toClear.forEach(index => {
    const r = Math.floor(index / BOARD_SIZE)
    const c = index % BOARD_SIZE
    board.value[r][c] = { type: -1, special: null }
  })
  
  matchedIndices.value.clear()
  await delay(200)
  await dropCells()
  fillNewCells()
  await delay(200)
  await checkChainReaction()
}

async function activateSpecialCombo(index1: number, index2: number) {
  const row1 = Math.floor(index1 / BOARD_SIZE)
  const col1 = index1 % BOARD_SIZE
  const row2 = Math.floor(index2 / BOARD_SIZE)
  const col2 = index2 % BOARD_SIZE
  
  const special1 = board.value[row1][col1].special
  const special2 = board.value[row2][col2].special
  
  combo.value += 2
  maxCombo.value = Math.max(maxCombo.value, combo.value)
  
  const toClear = new Set<number>()
  
  if ((special1 === SPECIAL.ROCKET_H || special1 === SPECIAL.ROCKET_V) &&
      (special2 === SPECIAL.ROCKET_H || special2 === SPECIAL.ROCKET_V)) {
    for (let c = 0; c < BOARD_SIZE; c++) toClear.add(row1 * BOARD_SIZE + c)
    for (let r = 0; r < BOARD_SIZE; r++) toClear.add(r * BOARD_SIZE + col1)
  } else if (special1 === SPECIAL.BOMB && special2 === SPECIAL.BOMB) {
    for (let r = Math.max(0, row1 - 2); r <= Math.min(BOARD_SIZE - 1, row1 + 2); r++) {
      for (let c = Math.max(0, col1 - 2); c <= Math.min(BOARD_SIZE - 1, col1 + 2); c++) {
        toClear.add(r * BOARD_SIZE + c)
      }
    }
  } else if (special1 === SPECIAL.RAINBOW || special2 === SPECIAL.RAINBOW) {
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
  } else {
    await activateSpecial(index1, index2)
    await activateSpecial(index2, index1)
    return
  }
  
  matchedIndices.value = toClear
  await delay(300)
  
  updateObjectives(toClear)
  score.value += toClear.size * 20 + comboBonus.value
  
  // 金币奖励
  earnedCoins.value += toClear.size * 2
  earnedCoins.value += combo.value * 5
  
  toClear.forEach(index => {
    const r = Math.floor(index / BOARD_SIZE)
    const c = index % BOARD_SIZE
    board.value[r][c] = { type: -1, special: null }
  })
  
  matchedIndices.value.clear()
  await delay(200)
  await dropCells()
  fillNewCells()
  await delay(200)
  await checkChainReaction()
}

async function processMatches() {
  const { matches, specialCells } = findMatches()
  
  if (matches.size === 0) {
    combo.value = 0
    isProcessing.value = false
    return
  }
  
  combo.value++
  maxCombo.value = Math.max(maxCombo.value, combo.value)
  
  matchedIndices.value = matches
  await delay(300)
  
  updateObjectives(matches)
  const baseScore = matches.size * 10
  score.value += baseScore + comboBonus.value
  
  // 金币奖励
  earnedCoins.value += matches.size
  earnedCoins.value += combo.value * 5
  
  const specialToCreate: { row: number, col: number, type: number, special: string }[] = []
  specialCells.forEach((special, index) => {
    const row = Math.floor(index / BOARD_SIZE)
    const col = index % BOARD_SIZE
    const type = board.value[row][col].type
    specialToCreate.push({ row, col, type, special })
  })
  
  matches.forEach(index => {
    const row = Math.floor(index / BOARD_SIZE)
    const col = index % BOARD_SIZE
    board.value[row][col] = { type: -1, special: null }
  })
  
  matchedIndices.value.clear()
  await delay(200)
  await dropCells()
  fillNewCells()
  await delay(200)
  
  specialToCreate.forEach(({ row, col, type, special }) => {
    board.value[row][col] = { type, special }
  })
  
  await processMatches()
}

async function checkChainReaction() {
  const { matches } = findMatches()
  if (matches.size > 0) {
    await processMatches()
  } else {
    combo.value = 0
    isProcessing.value = false
  }
}

async function dropCells() {
  fallingIndices.value.clear()
  
  for (let col = 0; col < BOARD_SIZE; col++) {
    let emptyRow = BOARD_SIZE - 1
    for (let row = BOARD_SIZE - 1; row >= 0; row--) {
      if (!board.value[row][col].isObstacle && board.value[row][col].type !== -1) {
        if (row !== emptyRow) {
          board.value[emptyRow][col] = { ...board.value[row][col] }
          board.value[row][col] = { type: -1, special: null }
          fallingIndices.value.add(emptyRow * BOARD_SIZE + col)
        }
        emptyRow--
      } else if (board.value[row][col].isObstacle) {
        emptyRow = row - 1
      }
    }
  }
  
  await delay(200)
  fallingIndices.value.clear()
}

function fillNewCells() {
  const level = currentLevel.value
  for (let row = 0; row < BOARD_SIZE; row++) {
    for (let col = 0; col < BOARD_SIZE; col++) {
      if (board.value[row][col].type === -1 && !board.value[row][col].isObstacle) {
        board.value[row][col] = {
          type: Math.floor(Math.random() * CELL_TYPES),
          special: null
        }
      }
    }
  }
}

function updateObjectives(matches: Set<number>) {
  const level = currentLevel.value
  
  matches.forEach(index => {
    const row = Math.floor(index / BOARD_SIZE)
    const col = index % BOARD_SIZE
    const cell = board.value[row][col]
    
    // 收集目标
    level.objectives.forEach(obj => {
      if (obj.type === 'collect' && obj.targetType === cell.type) {
        const key = 'collect_' + obj.targetType
        objectiveProgress.value[key] = (objectiveProgress.value[key] || 0) + 1
      }
    })
    
    // 清除障碍
    if (cell.isObstacle) {
      objectiveProgress.value['clear_obstacle'] = (objectiveProgress.value['clear_obstacle'] || 0) + 1
    }
  })
}

function checkEndConditions() {
  // 检查是否完成所有目标
  if (checkAllObjectives()) {
    levelComplete.value = true
    saveLevelProgress(currentLevel.value.id, earnedStars.value)
    return
  }
  
  // 检查是否步数用完
  if (movesLeft.value <= 0) {
    levelFailed.value = true
    failReason.value = '步数用完了'
    return
  }
  
  // 检查是否还有可移动
  if (!hasPossibleMoves()) {
    levelFailed.value = true
    failReason.value = '没有可移动的步数了'
    return
  }
}

function hasPossibleMoves(): boolean {
  for (let row = 0; row < BOARD_SIZE; row++) {
    for (let col = 0; col < BOARD_SIZE; col++) {
      if (board.value[row][col].isObstacle || board.value[row][col].type === -1) continue
      
      if (col < BOARD_SIZE - 1) {
        swapTemp(row, col, row, col + 1)
        const hasMatch = findMatches().matches.size > 0
        swapTemp(row, col, row, col + 1)
        if (hasMatch) return true
      }
      
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

function swapTemp(row1: number, col1: number, row2: number, col2: number) {
  const temp = { ...board.value[row1][col1] }
  board.value[row1][col1] = { ...board.value[row2][col2] }
  board.value[row2][col2] = temp
}

function getCellStyle(index: number) {
  const row = Math.floor(index / BOARD_SIZE)
  const col = index % BOARD_SIZE
  return { gridRow: row + 1, gridColumn: col + 1 }
}

function getSpecialIcon(special: string): string {
  const icons: Record<string, string> = {
    'bomb': '💣',
    'rocket_h': '➡️',
    'rocket_v': '⬇️',
    'rainbow': '🌈'
  }
  return icons[special] || ''
}

function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

function goBack() {
  // 保存金币
  shopStore.addCoins(earnedCoins.value)
  router.push('/game/match3-levels')
}

function restartLevel() {
  // 保存已获得的金币
  shopStore.addCoins(earnedCoins.value)
  initLevel()
}

function nextLevel() {
  // 保存金币并给通关奖励
  const levelBonus = earnedStars.value * 50 + movesLeft.value * 10
  shopStore.addCoins(earnedCoins.value + levelBonus)
  
  const nextId = currentLevel.value.id + 1
  if (nextId <= TOTAL_LEVELS) {
    router.push(`/game/match3-level/${nextId}`)
    initLevel()
  } else {
    router.push('/game/match3-levels')
  }
}

// 道具使用
function selectPowerUp(powerUpId: PowerUpType) {
  if (activePowerUp.value === powerUpId) {
    activePowerUp.value = null
  } else {
    activePowerUp.value = powerUpId
  }
}

// 使用锤子
async function useHammer(index: number) {
  if (!shopStore.usePowerUp('hammer')) return
  
  const row = Math.floor(index / BOARD_SIZE)
  const col = index % BOARD_SIZE
  
  // 消除该位置
  matchedIndices.value.add(index)
  await delay(300)
  
  // 如果是障碍物，清除它
  if (board.value[row][col].isObstacle) {
    board.value[row][col].isObstacle = false
    board.value[row][col].obstacleType = undefined
  }
  
  board.value[row][col] = { type: -1, special: null }
  matchedIndices.value.clear()
  
  // 奖励金币
  earnedCoins.value += 5
  
  await dropCells()
  fillNewCells()
  await delay(200)
  await checkChainReaction()
  
  activePowerUp.value = null
}

// 使用炸弹
async function useBomb(index: number) {
  if (!shopStore.usePowerUp('bomb')) return
  
  const centerRow = Math.floor(index / BOARD_SIZE)
  const centerCol = index % BOARD_SIZE
  
  const toClear = new Set<number>()
  
  // 3x3范围
  for (let r = Math.max(0, centerRow - 1); r <= Math.min(BOARD_SIZE - 1, centerRow + 1); r++) {
    for (let c = Math.max(0, centerCol - 1); c <= Math.min(BOARD_SIZE - 1, centerCol + 1); c++) {
      toClear.add(r * BOARD_SIZE + c)
    }
  }
  
  matchedIndices.value = toClear
  await delay(300)
  
  // 奖励金币
  earnedCoins.value += toClear.size * 2
  
  toClear.forEach(idx => {
    const r = Math.floor(idx / BOARD_SIZE)
    const c = idx % BOARD_SIZE
    if (board.value[r][c].isObstacle) {
      board.value[r][c].isObstacle = false
    }
    board.value[r][c] = { type: -1, special: null }
  })
  
  matchedIndices.value.clear()
  
  await dropCells()
  fillNewCells()
  await delay(200)
  await checkChainReaction()
  
  activePowerUp.value = null
}

// 使用刷新
async function useRefresh() {
  if (!shopStore.usePowerUp('refresh')) return
  
  // 重新生成棋盘（保留障碍物）
  const blockedCells: {row: number, col: number}[] = []
  for (let row = 0; row < BOARD_SIZE; row++) {
    for (let col = 0; col < BOARD_SIZE; col++) {
      if (board.value[row][col].isObstacle) {
        blockedCells.push({row, col})
      }
    }
  }
  
  board.value = generateBoard(blockedCells)
  
  // 确保没有初始匹配
  while (hasMatches().size > 0) {
    board.value = generateBoard(blockedCells)
  }
  
  activePowerUp.value = null
}

// 使用额外步数
function useExtraMoves() {
  if (!shopStore.usePowerUp('extra_moves')) return
  movesLeft.value += 5
  activePowerUp.value = null
}

// 使用提示
function useHint() {
  if (!shopStore.usePowerUp('hint')) return
  
  // 找到可移动的位置并高亮
  for (let row = 0; row < BOARD_SIZE; row++) {
    for (let col = 0; col < BOARD_SIZE; col++) {
      if (col < BOARD_SIZE - 1) {
        swapTemp(row, col, row, col + 1)
        if (findMatches().matches.size > 0) {
          swapTemp(row, col, row, col + 1)
          selectedIndex.value = row * BOARD_SIZE + col
          setTimeout(() => {
            selectedIndex.value = null
          }, 2000)
          activePowerUp.value = null
          return
        }
        swapTemp(row, col, row, col + 1)
      }
      if (row < BOARD_SIZE - 1) {
        swapTemp(row, col, row + 1, col)
        if (findMatches().matches.size > 0) {
          swapTemp(row, col, row + 1, col)
          selectedIndex.value = row * BOARD_SIZE + col
          setTimeout(() => {
            selectedIndex.value = null
          }, 2000)
          activePowerUp.value = null
          return
        }
        swapTemp(row, col, row + 1, col)
      }
    }
  }
  
  activePowerUp.value = null
}

// 修改点击处理，支持道具使用
const originalHandleMouseUp = handleMouseUp
handleMouseUp = function(index: number) {
  if (activePowerUp.value === 'hammer') {
    useHammer(index)
    return
  }
  if (activePowerUp.value === 'bomb') {
    useBomb(index)
    return
  }
  if (activePowerUp.value === 'refresh') {
    useRefresh()
    return
  }
  if (activePowerUp.value === 'extra_moves') {
    useExtraMoves()
    return
  }
  if (activePowerUp.value === 'hint') {
    useHint()
    return
  }
  originalHandleMouseUp(index)
}

onMounted(() => {
  initLevel()
})
</script>

<style scoped>
.match3-level {
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
  margin-bottom: 10px;
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

.level-info {
  text-align: right;
}

.level-name {
  display: block;
  color: #00f5ff;
  font-size: 0.9em;
}

.level-title {
  display: block;
  color: #fff;
  font-size: 1.1em;
  font-weight: bold;
}

.objectives-panel {
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 15px;
}

.objective {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.objective:last-child {
  border-bottom: none;
}

.objective.completed {
  opacity: 0.5;
}

.objective.completed .obj-text {
  color: #4ade80;
}

.obj-icon {
  font-size: 1.2em;
}

.obj-text {
  flex: 1;
  color: #fff;
  font-size: 0.9em;
}

.obj-progress {
  color: #00f5ff;
  font-weight: bold;
}

.moves-left {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.moves-label {
  color: #888;
  font-size: 0.9em;
}

.moves-value {
  font-size: 1.5em;
  font-weight: bold;
  color: #00f5ff;
}

.moves-value.warning {
  color: #facc15;
}

.moves-value.danger {
  color: #ff4444;
  animation: pulse 0.5s ease-in-out infinite alternate;
}

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
  box-shadow: 0 0 30px rgba(255, 0, 255, 0.5);
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
  text-shadow: 0 0 20px #ff00ff;
}

.bonus {
  display: block;
  color: #00f5ff;
  font-size: 1.5em;
  margin-top: 5px;
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
  box-shadow: 0 0 15px #ff4444;
  animation: bombPulse 0.8s ease-in-out infinite;
}

.cell.is-rocket-h, .cell.is-rocket-v {
  box-shadow: 0 0 15px #44ff44;
  animation: rocketGlow 1s ease-in-out infinite;
}

.cell.is-rainbow {
  box-shadow: 0 0 15px #ff00ff;
  animation: rainbowGlow 1.5s linear infinite;
}

.cell.is-obstacle {
  background: linear-gradient(135deg, #4a90e2, #2c5aa0);
  cursor: not-allowed;
}

.cell.is-swapping {
  animation: swapAnim 0.2s ease-in-out;
  z-index: 20;
}

.obstacle-icon {
  font-size: 1.5em;
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
  0%, 100% { box-shadow: 0 0 15px #44ff44; }
  50% { box-shadow: 0 0 25px #44ff44; }
}

@keyframes rainbowGlow {
  0% { filter: hue-rotate(0deg); }
  100% { filter: hue-rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 颜色 */
.color-0 { 
  background: linear-gradient(135deg, #ff6b8a, #ff8fa3);
}
.color-0::before {
  content: "🍓";
  font-size: 1.8em;
}
.color-1 { 
  background: linear-gradient(135deg, #7ee787, #4ade80);
}
.color-1::before {
  content: "🍀";
  font-size: 1.8em;
}
.color-2 { 
  background: linear-gradient(135deg, #67e8f9, #22d3ee);
}
.color-2::before {
  content: "💧";
  font-size: 1.8em;
}
.color-3 { 
  background: linear-gradient(135deg, #fde047, #facc15);
}
.color-3::before {
  content: "⭐";
  font-size: 1.8em;
}
.color-4 { 
  background: linear-gradient(135deg, #c084fc, #a855f7);
}
.color-4::before {
  content: "💎";
  font-size: 1.8em;
}
.color-5 { 
  background: linear-gradient(135deg, #fb923c, #f97316);
}
.color-5::before {
  content: "🥕";
  font-size: 1.8em;
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

.result-card {
  background: linear-gradient(135deg, #1a1a2e, #0a0a0a);
  border: 2px solid;
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  max-width: 350px;
}

.result-card.success {
  border-color: #4ade80;
  box-shadow: 0 0 30px rgba(74, 222, 128, 0.3);
}

.result-card.failure {
  border-color: #ff4444;
  box-shadow: 0 0 30px rgba(255, 68, 68, 0.3);
}

.result-card h2 {
  color: #fff;
  font-size: 1.8em;
  margin-bottom: 20px;
}

.stars {
  margin-bottom: 20px;
}

.star {
  font-size: 2em;
  opacity: 0.3;
  margin: 0 5px;
}

.star.earned {
  opacity: 1;
  animation: starPop 0.5s ease-out;
}

@keyframes starPop {
  0% { transform: scale(0); }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); }
}

.result-score, .result-moves {
  color: #00f5ff;
  font-size: 1.2em;
  margin-bottom: 10px;
}

.fail-reason {
  color: #ff8888;
  font-size: 1.1em;
  margin-bottom: 20px;
}

.result-buttons {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

.btn-primary, .btn-secondary {
  padding: 12px 30px;
  border: none;
  border-radius: 25px;
  font-size: 1em;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(45deg, #ff0066, #ff00ff);
  color: #fff;
}

.btn-primary:hover {
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(255, 0, 255, 0.5);
}

.btn-secondary {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #fff;
}

.btn-secondary:hover {
  border-color: #00f5ff;
  color: #00f5ff;
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
  
  .color-0::before, .color-1::before, .color-2::before,
  .color-3::before, .color-4::before, .color-5::before {
    font-size: 1.5em;
  }
}
</style>
