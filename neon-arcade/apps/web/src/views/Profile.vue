<template>
  <div class="profile-page">
    <!-- 背景 -->
    <div class="stars">
      <div v-for="i in 50" :key="i" class="star" :style="getStarStyle(i)"></div>
    </div>

    <!-- 头部 -->
    <header class="header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h1 class="title">个人中心</h1>
    </header>

    <!-- 用户信息卡片 -->
    <div class="user-card">
      <div class="avatar-section" @click="showAvatarPicker = true">
        <span class="avatar">{{ userStore.profile.avatar }}</span>
        <span class="edit-hint">点击修改</span>
      </div>
      
      <div class="info-section">
        <div class="nickname-row">
          <h2 v-if="!editingNickname" class="nickname" @click="startEditNickname">
            {{ userStore.profile.nickname }}
            <span class="edit-icon">✏️</span>
          </h2>
          <div v-else class="nickname-edit">
            <input 
              v-model="newNickname" 
              maxlength="20"
              @keyup.enter="saveNickname"
              @blur="saveNickname"
              ref="nicknameInput"
            />
          </div>
        </div>
        
        <div class="level-info">
          <span class="level-badge">Lv.{{ userStore.profile.level }}</span>
          <div class="exp-bar">
            <div class="exp-fill" :style="{ width: userStore.expProgress + '%' }"></div>
          </div>
          <span class="exp-text">{{ userStore.profile.exp }} / {{ userStore.expForNextLevel }}</span>
        </div>
        
        <div class="stats-row">
          <div class="stat">
            <span class="stat-value">{{ userStore.totalPlayCount }}</span>
            <span class="stat-label">游戏次数</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ formatTime(userStore.profile.totalPlayTime) }}</span>
            <span class="stat-label">游戏时长</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ joinedDays }}</span>
            <span class="stat-label">加入天数</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 成就展示 -->
    <div class="achievements-section">
      <h3 class="section-title">
        🏆 成就
        <span class="progress">{{ unlockedCount }} / {{ totalAchievements }}</span>
      </h3>
      
      <div class="achievements-grid">
        <div 
          v-for="achievement in userStore.achievements" 
          :key="achievement.id"
          class="achievement-card"
          :class="{ 'unlocked': isUnlocked(achievement.id) }"
          :title="achievement.description"
        >
          <span class="achievement-icon">{{ achievement.icon }}</span>
          <span class="achievement-name">{{ achievement.name }}</span>
        </div>
      </div>
    </div>

    <!-- 游戏统计 -->
    <div class="game-stats-section">
      <h3 class="section-title">🎮 游戏统计</h3>
      
      <div v-if="sortedStats.length === 0" class="empty-stats">
        <p>还没有游戏记录，快去玩游戏吧！</p>
      </div>
      
      <div v-else class="stats-list">
        <div 
          v-for="stat in sortedStats" 
          :key="stat.gameId"
          class="stat-item"
        >
          <div class="stat-game">
            <span class="game-name">{{ getGameName(stat.gameId) }}</span>
            <span class="play-count">{{ stat.playCount }} 次</span>
          </div>
          <div class="stat-scores">
            <div class="score-row">
              <span class="score-label">最高分</span>
              <span class="score-value high">{{ stat.highScore.toLocaleString() }}</span>
            </div>
            <div class="score-row">
              <span class="score-label">总分</span>
              <span class="score-value">{{ stat.totalScore.toLocaleString() }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 头像选择器 -->
    <div v-if="showAvatarPicker" class="avatar-modal" @click="showAvatarPicker = false">
      <div class="avatar-grid" @click.stop>
        <h3>选择头像</h3>
        <div class="avatars">
          <span 
            v-for="avatar in avatarOptions" 
            :key="avatar"
            class="avatar-option"
            :class="{ 'selected': avatar === userStore.profile.avatar }"
            @click="selectAvatar(avatar)"
          >
            {{ avatar }}
          </span>
        </div>
      </div>
    </div>

    <!-- 底部按钮 -->
    <div class="footer-actions">
      <button class="action-btn danger" @click="confirmReset">
        🗑️ 重置所有数据
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

// 加载用户数据
userStore.loadData()

// 昵称编辑
const editingNickname = ref(false)
const newNickname = ref('')
const nicknameInput = ref<HTMLInputElement>()

function startEditNickname() {
  newNickname.value = userStore.profile.nickname
  editingNickname.value = true
  nextTick(() => {
    nicknameInput.value?.focus()
  })
}

function saveNickname() {
  if (newNickname.value.trim()) {
    userStore.setNickname(newNickname.value.trim())
  }
  editingNickname.value = false
}

// 头像选择
const showAvatarPicker = ref(false)
const avatarOptions = ['🎮', '👾', '🕹️', '🎯', '🎲', '🎪', '🎨', '🎭', '👑', '🦁', '🐯', '🦊', '🐼', '🐨', '🐯', '🦄', '🌟', '🔥', '⚡', '💎']

function selectAvatar(avatar: string) {
  userStore.setAvatar(avatar)
  showAvatarPicker.value = false
}

// 成就
const unlockedCount = computed(() => userStore.unlockedAchievements.size)
const totalAchievements = computed(() => userStore.achievements.length)

function isUnlocked(achievementId: string): boolean {
  return userStore.isAchievementUnlocked(achievementId)
}

// 游戏统计
const sortedStats = computed(() => {
  return Object.values(userStore.gameStats)
    .sort((a, b) => b.playCount - a.playCount)
})

function getGameName(gameId: string): string {
  const names: Record<string, string> = {
    'snake': '贪吃蛇',
    'tetris': '俄罗斯方块',
    '2048': '2048',
    'airplane': '飞机大战',
    'whack-a-mole': '打地鼠',
    'sudoku': '霓虹数独',
    'match3': '霓虹消消乐'
  }
  return names[gameId] || gameId
}

// 加入天数
const joinedDays = computed(() => {
  const joined = new Date(userStore.profile.joinedAt)
  const now = new Date()
  return Math.floor((now.getTime() - joined.getTime()) / (1000 * 60 * 60 * 24))
})

// 格式化时间
function formatTime(minutes: number): string {
  if (minutes < 60) return minutes + '分钟'
  if (minutes < 1440) return Math.floor(minutes / 60) + '小时'
  return Math.floor(minutes / 1440) + '天'
}

// 星星样式
function getStarStyle(i: number) {
  return {
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    animationDelay: `${Math.random() * 2}s`
  }
}

// 返回
function goBack() {
  router.push('/')
}

// 重置数据
function confirmReset() {
  if (confirm('确定要重置所有数据吗？这将清除你的等级、成就和游戏记录，且无法恢复！')) {
    userStore.resetAllData()
    alert('数据已重置')
  }
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%);
  padding: 20px;
  position: relative;
}

.stars {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.star {
  position: absolute;
  width: 2px;
  height: 2px;
  background: #fff;
  border-radius: 50%;
  animation: twinkle 2s infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

.header {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}

.back-btn {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.back-btn:hover {
  border-color: #00f5ff;
  color: #00f5ff;
}

.title {
  flex: 1;
  text-align: center;
  font-size: 1.8em;
  background: linear-gradient(45deg, #00f5ff, #ff00ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-right: 80px;
}

.user-card {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 30px;
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: transform 0.3s;
}

.avatar-section:hover {
  transform: scale(1.05);
}

.avatar {
  font-size: 5em;
  margin-bottom: 10px;
}

.edit-hint {
  font-size: 0.8em;
  color: #888;
}

.info-section {
  flex: 1;
}

.nickname-row {
  margin-bottom: 20px;
}

.nickname {
  font-size: 1.8em;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
}

.edit-icon {
  font-size: 0.6em;
  opacity: 0.5;
}

.nickname-edit input {
  font-size: 1.5em;
  padding: 10px 15px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid #00f5ff;
  border-radius: 10px;
  color: #fff;
  outline: none;
}

.level-info {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.level-badge {
  padding: 5px 15px;
  background: linear-gradient(45deg, #ff0066, #ff00ff);
  border-radius: 20px;
  color: #fff;
  font-weight: bold;
}

.exp-bar {
  flex: 1;
  height: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  overflow: hidden;
}

.exp-fill {
  height: 100%;
  background: linear-gradient(90deg, #00f5ff, #00ff88);
  border-radius: 5px;
  transition: width 0.3s;
}

.exp-text {
  color: #888;
  font-size: 0.9em;
}

.stats-row {
  display: flex;
  gap: 30px;
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.5em;
  color: #00f5ff;
  font-weight: bold;
}

.stat-label {
  display: block;
  color: #888;
  font-size: 0.85em;
  margin-top: 5px;
}

.achievements-section,
.game-stats-section {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 25px;
  margin-bottom: 20px;
}

.section-title {
  color: #fff;
  font-size: 1.3em;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title .progress {
  color: #00f5ff;
  font-size: 0.9em;
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 15px;
}

.achievement-card {
  aspect-ratio: 1;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0.4;
  transition: all 0.3s;
}

.achievement-card.unlocked {
  opacity: 1;
  border-color: #ffd700;
  background: rgba(255, 215, 0, 0.1);
}

.achievement-icon {
  font-size: 2em;
}

.achievement-name {
  font-size: 0.75em;
  color: #fff;
  text-align: center;
}

.empty-stats {
  text-align: center;
  color: #666;
  padding: 40px;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stat-item {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 15px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-game {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.game-name {
  color: #fff;
  font-size: 1.1em;
}

.play-count {
  color: #888;
  font-size: 0.85em;
}

.stat-scores {
  display: flex;
  flex-direction: column;
  gap: 5px;
  text-align: right;
}

.score-row {
  display: flex;
  gap: 15px;
  align-items: center;
}

.score-label {
  color: #888;
  font-size: 0.85em;
}

.score-value {
  color: #fff;
  font-weight: bold;
}

.score-value.high {
  color: #00f5ff;
}

.avatar-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.avatar-grid {
  background: linear-gradient(135deg, #1a1a2e, #0a0a0a);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 30px;
  max-width: 400px;
  width: 90%;
}

.avatar-grid h3 {
  color: #fff;
  text-align: center;
  margin-bottom: 20px;
}

.avatars {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 15px;
}

.avatar-option {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2em;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.avatar-option:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.1);
}

.avatar-option.selected {
  border-color: #00f5ff;
  background: rgba(0, 245, 255, 0.2);
}

.footer-actions {
  position: relative;
  z-index: 1;
  text-align: center;
  margin-top: 30px;
}

.action-btn {
  padding: 12px 30px;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1em;
  transition: all 0.3s;
}

.action-btn.danger {
  background: rgba(255, 68, 68, 0.2);
  border: 1px solid rgba(255, 68, 68, 0.5);
  color: #ff8888;
}

.action-btn.danger:hover {
  background: rgba(255, 68, 68, 0.4);
}

@media (max-width: 768px) {
  .user-card {
    flex-direction: column;
    align-items: center;
  }
  
  .stats-row {
    justify-content: center;
  }
  
  .title {
    font-size: 1.4em;
    margin-right: 0;
  }
}</style>
