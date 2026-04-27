import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface UserProfile {
  id: string
  nickname: string
  avatar: string
  level: number
  exp: number
  totalPlayTime: number  // 分钟
  joinedAt: string
}

export interface GameStats {
  gameId: string
  playCount: number
  highScore: number
  totalScore: number
  lastPlayed: string
  playTime: number  // 分钟
}

export interface Achievement {
  id: string
  name: string
  description: string
  icon: string
  condition: string
  unlockedAt?: string
}

export const useUserStore = defineStore('user', () => {
  // ========== 用户档案 ==========
  const profile = ref<UserProfile>({
    id: generateUserId(),
    nickname: '玩家' + Math.floor(Math.random() * 9999),
    avatar: '🎮',
    level: 1,
    exp: 0,
    totalPlayTime: 0,
    joinedAt: new Date().toISOString()
  })

  // 等级配置
  const LEVEL_CONFIG = {
    maxLevel: 100,
    baseExp: 100,
    expMultiplier: 1.2
  }

  // 计算当前等级所需经验
  const expForNextLevel = computed(() => {
    return Math.floor(LEVEL_CONFIG.baseExp * Math.pow(LEVEL_CONFIG.expMultiplier, profile.value.level - 1))
  })

  // 经验进度百分比
  const expProgress = computed(() => {
    return Math.min(100, (profile.value.exp / expForNextLevel.value) * 100)
  })

  // ========== 游戏统计 ==========
  const gameStats = ref<Record<string, GameStats>>({})

  // 总游戏次数
  const totalPlayCount = computed(() => {
    return Object.values(gameStats.value).reduce((sum, stat) => sum + stat.playCount, 0)
  })

  // 最高分游戏
  const bestGame = computed(() => {
    const stats = Object.values(gameStats.value)
    if (stats.length === 0) return null
    return stats.reduce((best, current) => current.highScore > best.highScore ? current : best)
  })

  // ========== 成就系统 ==========
  const achievements = ref<Achievement[]>([
    // 游戏次数类
    { id: 'first_game', name: '初次体验', description: '完成第一局游戏', icon: '🎮', condition: 'playCount>=1' },
    { id: 'novice', name: '新手玩家', description: '累计完成10局游戏', icon: '🌱', condition: 'totalPlayCount>=10' },
    { id: 'regular', name: '常客', description: '累计完成50局游戏', icon: '🎯', condition: 'totalPlayCount>=50' },
    { id: 'addict', name: '游戏成瘾', description: '累计完成100局游戏', icon: '🔥', condition: 'totalPlayCount>=100' },
    { id: 'master', name: '游戏大师', description: '累计完成500局游戏', icon: '👑', condition: 'totalPlayCount>=500' },
    
    // 分数类
    { id: 'score_1000', name: '千分突破', description: '单局游戏达到1000分', icon: '💯', condition: 'singleScore>=1000' },
    { id: 'score_5000', name: '高分玩家', description: '单局游戏达到5000分', icon: '🏆', condition: 'singleScore>=5000' },
    { id: 'score_10000', name: '万分王者', description: '单局游戏达到10000分', icon: '👑', condition: 'singleScore>=10000' },
    
    // 游戏类型类
    { id: 'puzzle_fan', name: '益智爱好者', description: '玩过所有益智类游戏', icon: '🧩', condition: 'playAllPuzzle' },
    { id: 'action_fan', name: '动作达人', description: '玩过所有动作类游戏', icon: '⚡', condition: 'playAllAction' },
    { id: 'all_games', name: '全游戏制霸', description: '玩过所有游戏', icon: '🌟', condition: 'playAllGames' },
    
    // 特殊成就
    { id: 'night_owl', name: '夜猫子', description: '在凌晨0-5点玩游戏', icon: '🦉', condition: 'playAtNight' },
    { id: 'early_bird', name: '早起鸟', description: '在早上5-8点玩游戏', icon: '🐦', condition: 'playAtMorning' },
    { id: 'weekend_warrior', name: '周末战士', description: '在周末玩游戏', icon: '🎉', condition: 'playAtWeekend' },
    { id: 'persistent', name: '坚持不懈', description: '连续7天登录游戏', icon: '📅', condition: 'loginStreak>=7' },
    { id: 'collector', name: '收藏家', description: '解锁所有成就', icon: '🏅', condition: 'allAchievements' }
  ])

  // 已解锁的成就
  const unlockedAchievements = ref<Set<string>>(new Set())

  // 解锁成就
  function unlockAchievement(achievementId: string) {
    if (unlockedAchievements.value.has(achievementId)) return
    
    unlockedAchievements.value.add(achievementId)
    
    // 保存到本地存储
    saveAchievements()
    
    // 奖励经验
    addExp(50)
    
    // 触发成就解锁事件（可以被UI监听）
    window.dispatchEvent(new CustomEvent('achievement-unlocked', {
      detail: { achievementId }
    }))
  }

  // 检查成就是否解锁
  function isAchievementUnlocked(achievementId: string): boolean {
    return unlockedAchievements.value.has(achievementId)
  }

  // ========== 经验与等级 ==========
  function addExp(amount: number) {
    profile.value.exp += amount
    
    // 检查升级
    while (profile.value.exp >= expForNextLevel.value && profile.value.level < LEVEL_CONFIG.maxLevel) {
      profile.value.exp -= expForNextLevel.value
      profile.value.level++
      
      // 升级事件
      window.dispatchEvent(new CustomEvent('level-up', {
        detail: { level: profile.value.level }
      }))
    }
    
    saveProfile()
  }

  // ========== 游戏记录 ==========
  function recordGame(gameId: string, score: number, playTime: number = 0) {
    const now = new Date().toISOString()
    
    if (!gameStats.value[gameId]) {
      gameStats.value[gameId] = {
        gameId,
        playCount: 0,
        highScore: 0,
        totalScore: 0,
        lastPlayed: now,
        playTime: 0
      }
    }
    
    const stat = gameStats.value[gameId]
    stat.playCount++
    stat.totalScore += score
    stat.lastPlayed = now
    stat.playTime += playTime
    
    if (score > stat.highScore) {
      stat.highScore = score
    }
    
    // 增加经验
    const expGain = Math.floor(score / 100) + 10
    addExp(expGain)
    
    // 更新总游戏时间
    profile.value.totalPlayTime += playTime
    
    // 检查成就
    checkAchievements(score)
    
    saveStats()
    saveProfile()
  }

  // 检查成就条件
  function checkAchievements(singleScore: number) {
    const stats = Object.values(gameStats.value)
    const totalCount = stats.reduce((sum, s) => sum + s.playCount, 0)
    
    // 检查游戏次数成就
    if (totalCount >= 1) unlockAchievement('first_game')
    if (totalCount >= 10) unlockAchievement('novice')
    if (totalCount >= 50) unlockAchievement('regular')
    if (totalCount >= 100) unlockAchievement('addict')
    if (totalCount >= 500) unlockAchievement('master')
    
    // 检查分数成就
    if (singleScore >= 1000) unlockAchievement('score_1000')
    if (singleScore >= 5000) unlockAchievement('score_5000')
    if (singleScore >= 10000) unlockAchievement('score_10000')
    
    // 检查是否解锁了所有成就
    if (unlockedAchievements.value.size >= achievements.value.length - 1) {
      unlockAchievement('collector')
    }
  }

  // ========== 持久化 ==========
  function saveProfile() {
    localStorage.setItem('neon_arcade_profile', JSON.stringify(profile.value))
  }

  function saveStats() {
    localStorage.setItem('neon_arcade_stats', JSON.stringify(gameStats.value))
  }

  function saveAchievements() {
    localStorage.setItem('neon_arcade_achievements', JSON.stringify([...unlockedAchievements.value]))
  }

  function loadData() {
    // 加载档案
    const savedProfile = localStorage.getItem('neon_arcade_profile')
    if (savedProfile) {
      profile.value = JSON.parse(savedProfile)
    }
    
    // 加载统计
    const savedStats = localStorage.getItem('neon_arcade_stats')
    if (savedStats) {
      gameStats.value = JSON.parse(savedStats)
    }
    
    // 加载成就
    const savedAchievements = localStorage.getItem('neon_arcade_achievements')
    if (savedAchievements) {
      unlockedAchievements.value = new Set(JSON.parse(savedAchievements))
    }
  }

  // 生成用户ID
  function generateUserId(): string {
    const saved = localStorage.getItem('neon_arcade_user_id')
    if (saved) return saved
    
    const newId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem('neon_arcade_user_id', newId)
    return newId
  }

  // 修改昵称
  function setNickname(name: string) {
    profile.value.nickname = name.slice(0, 20)
    saveProfile()
  }

  // 修改头像
  function setAvatar(avatar: string) {
    profile.value.avatar = avatar
    saveProfile()
  }

  // 重置所有数据
  function resetAllData() {
    profile.value = {
      id: generateUserId(),
      nickname: '玩家' + Math.floor(Math.random() * 9999),
      avatar: '🎮',
      level: 1,
      exp: 0,
      totalPlayTime: 0,
      joinedAt: new Date().toISOString()
    }
    gameStats.value = {}
    unlockedAchievements.value = new Set()
    
    saveProfile()
    saveStats()
    saveAchievements()
  }

  return {
    // 状态
    profile,
    gameStats,
    achievements,
    unlockedAchievements,
    
    // 计算属性
    expForNextLevel,
    expProgress,
    totalPlayCount,
    bestGame,
    
    // 方法
    loadData,
    addExp,
    recordGame,
    unlockAchievement,
    isAchievementUnlocked,
    setNickname,
    setAvatar,
    resetAllData
  }
})
