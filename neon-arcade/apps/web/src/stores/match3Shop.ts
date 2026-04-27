import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 道具类型
export type PowerUpType = 'hammer' | 'refresh' | 'extra_moves' | 'rainbow_start' | 'bomb' | 'hint'

export interface PowerUp {
  id: PowerUpType
  name: string
  icon: string
  description: string
  price: number
  type: 'pre' | 'ingame'
  usable: boolean
}

export const POWER_UPS: PowerUp[] = [
  {
    id: 'hammer',
    name: '锤子',
    icon: '🔨',
    description: '消除任意一个元素或障碍物',
    price: 50,
    type: 'ingame',
    usable: true
  },
  {
    id: 'refresh',
    name: '刷新',
    icon: '🎲',
    description: '重新排列整个棋盘',
    price: 100,
    type: 'ingame',
    usable: true
  },
  {
    id: 'extra_moves',
    name: '额外步数',
    icon: '➕',
    description: '增加5步',
    price: 80,
    type: 'ingame',
    usable: true
  },
  {
    id: 'rainbow_start',
    name: '开局彩虹球',
    icon: '🌈',
    description: '开局自带一个彩虹球',
    price: 150,
    type: 'pre',
    usable: false
  },
  {
    id: 'bomb',
    name: '炸弹',
    icon: '💣',
    description: '消除3x3区域',
    price: 60,
    type: 'ingame',
    usable: true
  },
  {
    id: 'hint',
    name: '提示',
    icon: '💡',
    description: '显示一个可移动位置',
    price: 30,
    type: 'ingame',
    usable: true
  }
]

export const useMatch3ShopStore = defineStore('match3Shop', () => {
  // 金币数量
  const coins = ref(500) // 初始赠送500金币

  // 道具库存
  const inventory = ref<Record<PowerUpType, number>>({
    hammer: 0,
    refresh: 0,
    extra_moves: 0,
    rainbow_start: 0,
    bomb: 0,
    hint: 0
  })

  // 选中的开局道具
  const selectedPrePowerUp = ref<PowerUpType | null>(null)

  // 总道具数量
  const totalItems = computed(() => {
    return Object.values(inventory.value).reduce((sum, count) => sum + count, 0)
  })

  // 加载数据
  function loadData() {
    const savedCoins = localStorage.getItem('match3_coins')
    if (savedCoins) coins.value = parseInt(savedCoins)

    const savedInventory = localStorage.getItem('match3_inventory')
    if (savedInventory) inventory.value = JSON.parse(savedInventory)

    const savedSelected = localStorage.getItem('match3_selected_powerup')
    if (savedSelected) selectedPrePowerUp.value = savedSelected as PowerUpType
  }

  // 保存数据
  function saveData() {
    localStorage.setItem('match3_coins', coins.value.toString())
    localStorage.setItem('match3_inventory', JSON.stringify(inventory.value))
    if (selectedPrePowerUp.value) {
      localStorage.setItem('match3_selected_powerup', selectedPrePowerUp.value)
    } else {
      localStorage.removeItem('match3_selected_powerup')
    }
  }

  // 添加金币
  function addCoins(amount: number) {
    coins.value += amount
    saveData()
  }

  // 消费金币
  function spendCoins(amount: number): boolean {
    if (coins.value < amount) return false
    coins.value -= amount
    saveData()
    return true
  }

  // 购买道具
  function buyPowerUp(powerUpId: PowerUpType, quantity: number = 1): boolean {
    const powerUp = POWER_UPS.find(p => p.id === powerUpId)
    if (!powerUp) return false

    const totalPrice = powerUp.price * quantity
    if (!spendCoins(totalPrice)) return false

    inventory.value[powerUpId] += quantity
    saveData()
    return true
  }

  // 使用道具
  function usePowerUp(powerUpId: PowerUpType): boolean {
    if (inventory.value[powerUpId] <= 0) return false
    inventory.value[powerUpId]--
    saveData()
    return true
  }

  // 选择开局道具
  function selectPrePowerUp(powerUpId: PowerUpType | null) {
    selectedPrePowerUp.value = powerUpId
    saveData()
  }

  // 获取道具数量
  function getPowerUpCount(powerUpId: PowerUpType): number {
    return inventory.value[powerUpId]
  }

  // 重置数据（调试用）
  function resetData() {
    coins.value = 500
    inventory.value = {
      hammer: 0,
      refresh: 0,
      extra_moves: 0,
      rainbow_start: 0,
      bomb: 0,
      hint: 0
    }
    selectedPrePowerUp.value = null
    saveData()
  }

  return {
    coins,
    inventory,
    selectedPrePowerUp,
    totalItems,
    loadData,
    addCoins,
    spendCoins,
    buyPowerUp,
    usePowerUp,
    selectPrePowerUp,
    getPowerUpCount,
    resetData
  }
})
