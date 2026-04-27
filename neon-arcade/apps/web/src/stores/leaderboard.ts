import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface LeaderboardEntry {
  rank: number
  userId: string
  nickname: string
  avatar: string
  score: number
  gameId?: string
  gameName?: string
  achievedAt: string
}

export interface GameLeaderboard {
  gameId: string
  gameName: string
  entries: LeaderboardEntry[]
}

// 模拟其他玩家数据
const MOCK_PLAYERS = [
  { nickname: '霓虹之王', avatar: '👑' },
  { nickname: '消消乐大师', avatar: '💎' },
  { nickname: '方块达人', avatar: '🧱' },
  { nickname: '贪吃蛇霸主', avatar: '🐍' },
  { nickname: '飞机战神', avatar: '✈️' },
  { nickname: '数独天才', avatar: '🧩' },
  { nickname: '反应超人', avatar: '⚡' },
  { nickname: '游戏狂魔', avatar: '🔥' },
  { nickname: '休闲玩家', avatar: '😎' },
  { nickname: '新手小白', avatar: '🌱' }
]

export const useLeaderboardStore = defineStore('leaderboard', () => {
  // 游戏列表
  const games = ref([
    { id: 'snake', name: '贪吃蛇' },
    { id: 'tetris', name: '俄罗斯方块' },
    { id: '2048', name: '2048' },
    { id: 'airplane', name: '飞机大战' },
    { id: 'whack-a-mole', name: '打地鼠' },
    { id: 'sudoku', name: '霓虹数独' },
    { id: 'match3', name: '霓虹消消乐' }
  ])

  // 各游戏排行榜数据（本地模拟）
  const leaderboards = ref<Record<string, LeaderboardEntry[]>>({})

  // 当前选中的游戏
  const selectedGame = ref('all')

  // 排行榜类型
  const leaderboardTypes = [
    { id: 'all', name: '总排行' },
    { id: 'snake', name: '贪吃蛇' },
    { id: 'tetris', name: '俄罗斯方块' },
    { id: '2048', name: '2048' },
    { id: 'airplane', name: '飞机大战' },
    { id: 'whack-a-mole', name: '打地鼠' },
    { id: 'sudoku', name: '霓虹数独' },
    { id: 'match3', name: '霓虹消消乐' }
  ]

  // 当前显示的排行榜
  const currentLeaderboard = computed((): LeaderboardEntry[] => {
    if (selectedGame.value === 'all') {
      // 总排行 - 合并所有游戏最高分
      return getOverallLeaderboard()
    }
    return leaderboards.value[selectedGame.value] || []
  })

  // 获取总排行榜
  function getOverallLeaderboard(): LeaderboardEntry[] {
    const allScores: LeaderboardEntry[] = []
    
    // 收集所有游戏的最高分
    Object.entries(leaderboards.value).forEach(([gameId, entries]) => {
      const game = games.value.find(g => g.id === gameId)
      entries.slice(0, 3).forEach((entry, index) => {
        allScores.push({
          ...entry,
          rank: index + 1,
          gameId,
          gameName: game?.name
        })
      })
    })
    
    // 按分数排序
    allScores.sort((a, b) => b.score - a.score)
    
    // 重新分配排名
    return allScores.slice(0, 20).map((entry, index) => ({
      ...entry,
      rank: index + 1
    }))
  }

  // 获取用户排名
  function getUserRank(userId: string, gameId: string = 'all'): number {
    const board = gameId === 'all' ? getOverallLeaderboard() : (leaderboards.value[gameId] || [])
    const entry = board.find(e => e.userId === userId)
    return entry?.rank || 0
  }

  // 提交分数到排行榜
  function submitScore(userId: string, nickname: string, avatar: string, gameId: string, score: number) {
    const game = games.value.find(g => g.id === gameId)
    if (!game) return

    // 确保该游戏有排行榜
    if (!leaderboards.value[gameId]) {
      leaderboards.value[gameId] = generateMockLeaderboard(gameId, game.name)
    }

    const board = leaderboards.value[gameId]
    
    // 检查是否已有该用户记录
    const existingIndex = board.findIndex(e => e.userId === userId)
    
    const newEntry: LeaderboardEntry = {
      rank: 0,
      userId,
      nickname,
      avatar,
      score,
      gameId,
      gameName: game.name,
      achievedAt: new Date().toISOString()
    }

    if (existingIndex >= 0) {
      // 更新分数（只保留更高分）
      if (score > board[existingIndex].score) {
        board[existingIndex] = newEntry
      }
    } else {
      // 添加新记录
      board.push(newEntry)
    }

    // 重新排序
    board.sort((a, b) => b.score - a.score)
    
    // 重新分配排名
    board.forEach((entry, index) => {
      entry.rank = index + 1
    })

    // 只保留前100名
    leaderboards.value[gameId] = board.slice(0, 100)

    // 保存到本地存储
    saveLeaderboards()

    return board.find(e => e.userId === userId)?.rank || 0
  }

  // 生成模拟排行榜数据
  function generateMockLeaderboard(gameId: string, gameName: string): LeaderboardEntry[] {
    const entries: LeaderboardEntry[] = []
    
    // 基础分数范围
    const baseScores: Record<string, number> = {
      'snake': 5000,
      'tetris': 10000,
      '2048': 50000,
      'airplane': 5000,
      'whack-a-mole': 3000,
      'sudoku': 2000,
      'match3': 15000
    }
    
    const baseScore = baseScores[gameId] || 5000
    
    for (let i = 0; i < 20; i++) {
      const player = MOCK_PLAYERS[i % MOCK_PLAYERS.length]
      const score = Math.floor(baseScore * (1 + Math.random() * 2) * (20 - i) / 20)
      
      entries.push({
        rank: i + 1,
        userId: 'mock_' + i,
        nickname: player.nickname,
        avatar: player.avatar,
        score,
        gameId,
        gameName,
        achievedAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString()
      })
    }
    
    return entries
  }

  // 选择游戏
  function selectGame(gameId: string) {
    selectedGame.value = gameId
    
    // 如果是具体游戏，确保有排行榜数据
    if (gameId !== 'all' && !leaderboards.value[gameId]) {
      const game = games.value.find(g => g.id === gameId)
      if (game) {
        leaderboards.value[gameId] = generateMockLeaderboard(gameId, game.name)
      }
    }
  }

  // 格式化分数
  function formatScore(score: number): string {
    if (score >= 1000000) {
      return (score / 1000000).toFixed(1) + 'M'
    }
    if (score >= 1000) {
      return (score / 1000).toFixed(1) + 'K'
    }
    return score.toString()
  }

  // 格式化时间
  function formatTime(isoString: string): string {
    const date = new Date(isoString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)
    
    if (minutes < 1) return '刚刚'
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 30) return `${days}天前`
    return date.toLocaleDateString('zh-CN')
  }

  // 保存到本地存储
  function saveLeaderboards() {
    localStorage.setItem('neon_arcade_leaderboards', JSON.stringify(leaderboards.value))
  }

  // 从本地存储加载
  function loadLeaderboards() {
    const saved = localStorage.getItem('neon_arcade_leaderboards')
    if (saved) {
      leaderboards.value = JSON.parse(saved)
    } else {
      // 初始化所有游戏的排行榜
      games.value.forEach(game => {
        leaderboards.value[game.id] = generateMockLeaderboard(game.id, game.name)
      })
    }
  }

  return {
    games,
    leaderboards,
    selectedGame,
    leaderboardTypes,
    currentLeaderboard,
    selectGame,
    submitScore,
    getUserRank,
    formatScore,
    formatTime,
    loadLeaderboards
  }
})
