<template>
  <div class="match3-shop">
    <!-- 顶部 -->
    <div class="shop-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h1 class="shop-title">道具商店</h1>
      <div class="coins">
        <span class="coin-icon">💰</span>
        <span class="coin-amount">{{ shopStore.coins }}</span>
      </div>
    </div>

    <!-- 道具列表 -->
    <div class="powerups-grid">
      <div 
        v-for="powerUp in POWER_UPS" 
        :key="powerUp.id"
        class="powerup-card"
        :class="{ 'pre-game': powerUp.type === 'pre' }"
      >
        <div class="powerup-icon">{{ powerUp.icon }}</div>
        <h3 class="powerup-name">{{ powerUp.name }}</h3>
        <p class="powerup-desc">{{ powerUp.description }}</p>
        <div class="powerup-type">{{ powerUp.type === 'pre' ? '开局道具' : '局内道具' }}</div>
        
        <div class="powerup-actions">
          <div class="owned-count">
            拥有: {{ shopStore.getPowerUpCount(powerUp.id) }}
          </div>
          <div class="buy-section">
            <span class="price">{{ powerUp.price }} 💰</span>
            <button 
              class="buy-btn"
              :disabled="shopStore.coins < powerUp.price"
              @click="buy(powerUp.id)"
            >
              购买
            </button>
          </div>
        </div>

        <!-- 开局道具选择 -->
        <div v-if="powerUp.type === 'pre'" class="pre-select">
          <label class="checkbox">
            <input 
              type="checkbox" 
              :checked="shopStore.selectedPrePowerUp === powerUp.id"
              @change="togglePrePowerUp(powerUp.id)"
            />
            <span>开局使用</span>
          </label>
        </div>
      </div>
    </div>

    <!-- 获取金币提示 -->
    <div class="earn-coins">
      <h3>💡 如何获得金币？</h3>
      <ul>
        <li>每消除1个元素 +1金币</li>
        <li>完成关卡获得基础奖励</li>
        <li>连击奖励：连击数 × 5金币</li>
        <li>每日登录 +100金币</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMatch3ShopStore, POWER_UPS } from '../stores/match3Shop'

const router = useRouter()
const shopStore = useMatch3ShopStore()

onMounted(() => {
  shopStore.loadData()
})

function buy(powerUpId: string) {
  if (shopStore.buyPowerUp(powerUpId as any)) {
    // 购买成功动画或提示
  }
}

function togglePrePowerUp(powerUpId: string) {
  if (shopStore.selectedPrePowerUp === powerUpId) {
    shopStore.selectPrePowerUp(null)
  } else {
    shopStore.selectPrePowerUp(powerUpId as any)
  }
}

function goBack() {
  router.push('/game/match3')
}
</script>

<style scoped>
.match3-shop {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%);
  padding: 20px;
}

.shop-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.shop-title {
  font-size: 1.8em;
  background: linear-gradient(45deg, #ffd700, #ffed4a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.coins {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 215, 0, 0.1);
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 25px;
}

.coin-icon {
  font-size: 1.3em;
}

.coin-amount {
  color: #ffd700;
  font-size: 1.2em;
  font-weight: bold;
}

.powerups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  max-width: 1000px;
  margin: 0 auto 30px;
}

.powerup-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 25px;
  text-align: center;
  transition: all 0.3s;
}

.powerup-card:hover {
  transform: translateY(-5px);
  border-color: rgba(255, 255, 255, 0.2);
}

.powerup-card.pre-game {
  border-color: rgba(255, 0, 255, 0.3);
}

.powerup-card.pre-game:hover {
  border-color: rgba(255, 0, 255, 0.5);
}

.powerup-icon {
  font-size: 3.5em;
  margin-bottom: 10px;
}

.powerup-name {
  color: #fff;
  font-size: 1.3em;
  margin-bottom: 8px;
}

.powerup-desc {
  color: #888;
  font-size: 0.9em;
  margin-bottom: 10px;
  line-height: 1.4;
}

.powerup-type {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  color: #aaa;
  font-size: 0.8em;
  margin-bottom: 15px;
}

.powerup-card.pre-game .powerup-type {
  background: rgba(255, 0, 255, 0.2);
  color: #ff00ff;
}

.powerup-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.owned-count {
  color: #00f5ff;
  font-size: 0.9em;
}

.buy-section {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
}

.price {
  color: #ffd700;
  font-weight: bold;
}

.buy-btn {
  padding: 8px 20px;
  background: linear-gradient(45deg, #00f5ff, #00ff88);
  border: none;
  border-radius: 20px;
  color: #0a0a0a;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.buy-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
}

.buy-btn:disabled {
  background: #444;
  color: #888;
  cursor: not-allowed;
}

.pre-select {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.checkbox {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #fff;
  cursor: pointer;
}

.checkbox input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.earn-coins {
  max-width: 600px;
  margin: 0 auto;
  padding: 25px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  text-align: center;
}

.earn-coins h3 {
  color: #fff;
  margin-bottom: 15px;
}

.earn-coins ul {
  list-style: none;
  padding: 0;
}

.earn-coins li {
  color: #888;
  padding: 8px 0;
}

@media (max-width: 768px) {
  .shop-title {
    font-size: 1.3em;
  }
  
  .coins {
    padding: 8px 15px;
  }
  
  .coin-amount {
    font-size: 1em;
  }
  
  .powerups-grid {
    grid-template-columns: 1fr;
  }
}
</style>
