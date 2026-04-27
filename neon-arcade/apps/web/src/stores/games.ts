import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Game {
  id: string
  name: string
  icon: string
  description: string
  category: string
  categoryLabel: string
  path: string
  color: [string, string]
  difficulty?: 'easy' | 'medium' | 'hard'
}

export const useGamesStore = defineStore('games', () => {
  // 游戏列表
  const games = ref<Game[]>([
    {
      id: 'snake',
      name: '贪吃蛇',
      icon: '🐍',
      description: '经典贪吃蛇游戏，霓虹发光效果，吃食物变长，挑战最高分！',
      category: 'classic',
      categoryLabel: '经典',
      path: '/games/snake',
      color: ['#00f5ff', '#0080ff']
    },
    {
      id: 'tetris',
      name: '俄罗斯方块',
      icon: '🎮',
      description: '永恒的益智经典，消除行数得分，速度会越来越快！',
      category: 'puzzle',
      categoryLabel: '益智',
      path: '/games/tetris',
      color: ['#ff00ff', '#ff0066']
    },
    {
      id: '2048',
      name: '2048',
      icon: '🔢',
      description: '滑动合并数字，目标是达到2048，考验你的策略思维！',
      category: 'puzzle',
      categoryLabel: '益智',
      path: '/games/2048',
      color: ['#ffcc00', '#ff6600']
    },
    {
      id: 'airplane',
      name: '飞机大战',
      icon: '✈️',
      description: '操控战机躲避敌机，发射子弹消灭敌人，保卫领空！',
      category: 'action',
      categoryLabel: '动作',
      path: '/games/airplane',
      color: ['#00ff88', '#00f5ff']
    },
    {
      id: 'whack-a-mole',
      name: '打地鼠',
      icon: '🔨',
      description: '经典打地鼠游戏，三种难度可选，连击得分更高！',
      category: 'reaction',
      categoryLabel: '反应',
      path: '/games/whack-a-mole',
      color: ['#8B4513', '#D2691E']
    },
    {
      id: 'sudoku',
      name: '霓虹数独',
      icon: '🧩',
      description: '经典数独闯关，三种难度，每日挑战，道具提示助你通关！',
      category: 'puzzle',
      categoryLabel: '益智',
      path: '/games/sudoku',
      color: ['#9b59b6', '#e74c3c']
    },
    {
      id: 'match3',
      name: '霓虹消消乐',
      icon: '💎',
      description: '经典三消游戏，交换元素消除，连击得分，挑战最高分！',
      category: 'puzzle',
      categoryLabel: '益智',
      path: '/games/match3',
      color: ['#ff0066', '#ff00ff']
    }
  ])

  // 分类列表
  const categories = [
    { id: 'all', label: '全部' },
    { id: 'puzzle', label: '益智' },
    { id: 'action', label: '动作' },
    { id: 'classic', label: '经典' },
    { id: 'reaction', label: '反应' }
  ]

  // 当前选中的分类
  const activeCategory = ref('all')

  // 搜索关键词
  const searchKeyword = ref('')

  // 过滤后的游戏列表
  const filteredGames = computed(() => {
    return games.value.filter(game => {
      const matchesCategory = activeCategory.value === 'all' || game.category === activeCategory.value
      const matchesSearch = !searchKeyword.value || 
        game.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        game.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
      return matchesCategory && matchesSearch
    })
  })

  // 设置分类
  function setCategory(category: string) {
    activeCategory.value = category
  }

  // 设置搜索关键词
  function setSearch(keyword: string) {
    searchKeyword.value = keyword
  }

  return {
    games,
    categories,
    activeCategory,
    searchKeyword,
    filteredGames,
    setCategory,
    setSearch
  }
})
