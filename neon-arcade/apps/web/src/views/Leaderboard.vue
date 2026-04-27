<template>
  <div class="leaderboard-page">
    <!-- 背景 -->
    <div class="stars">
      <div v-for="i in 50" :key="i" class="star" :style="getStarStyle(i)"></div>
    </div>

    <!-- 头部 -->
    <header class="header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h1 class="title">🏆 排行榜</h1>
    </header>

    <!-- 游戏选择 -->
    <div class="game-tabs">
      <button
        v-for="type in leaderboardStore.leaderboardTypes"
        :key="type.id"
        class="tab-btn"
        :class="{ active: leaderboardStore.selectedGame === type.id }"
        @click="selectGame(type.id)"
      >
        {{ type.name }}
      </button>
    </div>

    <!-- 前三名 podium -->
    <div class="podium" v-if="topThree.length > 0">
      <div class="podium-item second" v-if="topThree[1]">
        <div class="rank-badge">2</div>
        <span class="podium-avatar">{{ topThree[1].avatar }}</span>
        <span class="podium-name">{{ topThree[1].nickname }}</span>
        <span class="podium-score">{{ formatScore(topThree[1].score) }}</span>
      </div>
      <div class="podium-item first" v-if="topThree[0]">
        <div class="rank-badge">👑</div>
        <span class="podium-avatar">{{ topThree[0].avatar }}</span>
        <span class="podium-name">{{ topThree[0].nickname }}</span>
        <span class="podium-score">{{ formatScore(topThree[0].score) }}</span>
      </div>
      <div class="podium-item third" v-if="topThree[2]">
        <div class="rank-badge">3</div>
        <span class="podium-avatar">{{ topThree[2].avatar }}</span>
        <span class="podium-name">{{ topThree[2].nickname }}</span>
        <span class="podium-score">{{ formatScore(topThree[2].score) }}</span>
      </div>
    </div>

    <!-- 排行榜列表 -->
    <div class="leaderboard-list">
      <div 
        v-for="entry in otherEntries" 
        :key="entry.userId + entry.gameId"
        class="list-item"
        :class="{ 'is-me': isCurrentUser(entry.userId) }"
      >
        <span class="list-rank">{{ entry.rank }}</span>
        <span class="list-avatar">{{ entry.avatar }}</span>
        <div class="list-info">
          <span class="list-name">{{ entry.nickname }}</span>
          <span v-if="entry.gameName" class="list-game">{{ entry.gameName }}</span>
        </div>
        <span class="list-score">{{ formatScore(entry.score) }}</span>
        <span class="list-time">{{ formatTime(entry.achievedAt) }}</span>
      </div>
    </div>

    <!-- 我的排名 -->
    <div class="my-rank" v-if="myRank > 0">
      <span class="rank-label">我的排名</span>
      <span class="rank-value">#{{ myRank }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLeaderboardStore } from '../stores/leaderboard'
import { useUserStore } from '../stores/user'

const router = useRouter()
const leaderboardStore = useLeaderboardStore()
const userStore = useUserStore()

// 加载数据
onMounted(() => {
  leaderboardStore.loadLeaderboards()
  userStore.loadData()
})

// 前三名
const topThree = computed(() => {
  return leaderboardStore.currentLeaderboard.slice(0, 3)
})

// 其他排名
const otherEntries = computed(() => {
  return leaderboardStore.currentLeaderboard.slice(3)
})

// 我的排名
const myRank = computed(() => {
  return leaderboardStore.getUserRank(userStore.profile.id, leaderboardStore.selectedGame)
})

// 选择游戏
function selectGame(gameId: string) {
  leaderboardStore.selectGame(gameId)
}

// 格式化分数
function formatScore(score: number): string {
  return leaderboardStore.formatScore(score)
}

// 格式化时间
function formatTime(isoString: string): string {
  return leaderboardStore.formatTime(isoString)
}

// 是否当前用户
function isCurrentUser(userId: string): boolean {
  return userId === userStore.profile.id
}

// 返回
function goBack() {
  router.push('/')
}

// 星星样式
function getStarStyle(i: number) {
  return {
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    animationDelay: `${Math.random() * 2}s`
  }
}
</script>

<style scoped>
.leaderboard-page {
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
  margin-bottom: 20px;
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
  background: linear-gradient(45deg, #ffd700, #ffed4a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-right: 80px;
}

.game-tabs {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.tab-btn {
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  color: #888;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.tab-btn:hover,
.tab-btn.active {
  background: rgba(255, 215, 0, 0.2);
  border-color: #ffd700;
  color: #ffd700;
}

.podium {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 20px;
  margin-bottom: 30px;
  padding: 20px;
}

.podium-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 20px;
  min-width: 100px;
}

.podium-item.first {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 215, 0, 0.05));
  border: 2px solid #ffd700;
  transform: scale(1.1);
  z-index: 2;
}

.podium-item.second {
  background: linear-gradient(135deg, rgba(192, 192, 192, 0.2), rgba(192, 192, 192, 0.05));
  border: 2px solid #c0c0c0;
}

.podium-item.third {
  background: linear-gradient(135deg, rgba(205, 127, 50, 0.2), rgba(205, 127, 50, 0.05));
  border: 2px solid #cd7f32;
}

.rank-badge {
  font-size: 1.5em;
  font-weight: bold;
  margin-bottom: 10px;
}

.podium-avatar {
  font-size: 3em;
  margin-bottom: 10px;
}

.podium-name {
  color: #fff;
  font-weight: bold;
  margin-bottom: 5px;
  text-align: center;
}

.podium-score {
  color: #ffd700;
  font-size: 1.2em;
}

.leaderboard-list {
  position: relative;
  z-index: 1;
  max-width: 600px;
  margin: 0 auto;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 15px;
  margin-bottom: 10px;
  transition: all 0.3s;
}

.list-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.list-item.is-me {
  background: rgba(0, 245, 255, 0.1);
  border: 1px solid rgba(0, 245, 255, 0.3);
}

.list-rank {
  width: 30px;
  text-align: center;
  color: #888;
  font-weight: bold;
}

.list-avatar {
  font-size: 1.8em;
}

.list-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.list-name {
  color: #fff;
  font-weight: bold;
}

.list-game {
  color: #888;
  font-size: 0.8em;
}

.list-score {
  color: #ffd700;
  font-weight: bold;
  font-size: 1.1em;
}

.list-time {
  color: #666;
  font-size: 0.75em;
  min-width: 60px;
  text-align: right;
}

.my-rank {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(45deg, #ff0066, #ff00ff);
  padding: 15px 40px;
  border-radius: 30px;
  display: flex;
  gap: 15px;
  align-items: center;
  box-shadow: 0 10px 30px rgba(255, 0, 255, 0.3);
}

.rank-label {
  color: rgba(255, 255, 255, 0.8);
}

.rank-value {
  color: #fff;
  font-size: 1.3em;
  font-weight: bold;
}

@media (max-width: 768px) {
  .title {
    font-size: 1.4em;
    margin-right: 0;
  }
  
  .podium {
    gap: 10px;
  }
  
  .podium-item {
    min-width: 80px;
    padding: 15px;
  }
  
  .podium-avatar {
    font-size: 2em;
  }
  
  .list-item {
    padding: 12px 15px;
  }
  
  .list-time {
    display: none;
  }
}</style>
