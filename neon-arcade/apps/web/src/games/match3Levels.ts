// 三消闯关模式 - 关卡配置

export type ObjectiveType = 
  | 'score'           // 达到指定分数
  | 'collect'         // 收集指定类型的元素
  | 'clear_obstacle'  // 清除障碍物
  | 'drop_items'      // 让指定物品掉到底部
  | 'combo'           // 达成指定连击数
  | 'special'         // 使用指定数量的特殊道具

export interface LevelObjective {
  type: ObjectiveType
  target: number
  targetType?: number  // 用于 collect 类型，指定收集哪种元素
  description?: string
}

export interface CellConfig {
  type: number
  special?: string
  isObstacle?: boolean
  obstacleType?: string
}

export interface Level {
  id: number
  name: string
  description: string
  moves: number
  objectives: LevelObjective[]
  starRequirements: [number, number, number]  // 1星、2星、3星分数要求
  customBoard?: CellConfig[][]  // 自定义棋盘，不设置则随机生成
  blockedCells?: {row: number, col: number}[]  // 阻挡格位置
  availableColors?: number[]  // 可用的颜色类型，不设置则全部可用
}

// 关卡数据
export const LEVELS: Level[] = [
  // 第1关：入门教学 - 简单分数目标
  {
    id: 1,
    name: "初入霓虹",
    description: "达到1000分即可过关",
    moves: 15,
    objectives: [
      { type: 'score', target: 1000, description: '达到1000分' }
    ],
    starRequirements: [1000, 2000, 3500]
  },
  
  // 第2关：收集挑战
  {
    id: 2,
    name: "草莓大丰收",
    description: "收集20个草莓",
    moves: 18,
    objectives: [
      { type: 'collect', target: 20, targetType: 0, description: '收集20个草莓 🍓' },
      { type: 'score', target: 1500, description: '达到1500分' }
    ],
    starRequirements: [1500, 3000, 5000]
  },
  
  // 第3关：障碍物初现
  {
    id: 3,
    name: "破冰行动",
    description: "清除所有冰块",
    moves: 20,
    objectives: [
      { type: 'clear_obstacle', target: 8, description: '清除8个冰块' }
    ],
    starRequirements: [2000, 4000, 6000],
    blockedCells: [
      {row: 3, col: 3}, {row: 3, col: 4},
      {row: 4, col: 3}, {row: 4, col: 4},
      {row: 2, col: 2}, {row: 2, col: 5},
      {row: 5, col: 2}, {row: 5, col: 5}
    ]
  },
  
  // 第4关：连击挑战
  {
    id: 4,
    name: "连击大师",
    description: "达成5连击",
    moves: 15,
    objectives: [
      { type: 'combo', target: 5, description: '达成5连击' },
      { type: 'score', target: 2500, description: '达到2500分' }
    ],
    starRequirements: [2500, 4500, 7000]
  },
  
  // 第5关：综合挑战
  {
    id: 5,
    name: "霓虹试炼",
    description: "收集草莓和四叶草，清除冰块",
    moves: 25,
    objectives: [
      { type: 'collect', target: 15, targetType: 0, description: '收集15个草莓 🍓' },
      { type: 'collect', target: 15, targetType: 1, description: '收集15个四叶草 🍀' },
      { type: 'clear_obstacle', target: 6, description: '清除6个冰块' }
    ],
    starRequirements: [3000, 5500, 8000],
    blockedCells: [
      {row: 2, col: 2}, {row: 2, col: 5},
      {row: 5, col: 2}, {row: 5, col: 5},
      {row: 3, col: 3}, {row: 4, col: 4}
    ]
  },
  
  // 第6关：特殊道具
  {
    id: 6,
    name: "道具大师",
    description: "使用5个特殊道具",
    moves: 20,
    objectives: [
      { type: 'special', target: 5, description: '使用5个特殊道具' },
      { type: 'score', target: 3000, description: '达到3000分' }
    ],
    starRequirements: [3000, 5000, 7500]
  },
  
  // 第7关：掉落物品
  {
    id: 7,
    name: "宝石收集",
    description: "让3个宝石掉到底部",
    moves: 22,
    objectives: [
      { type: 'drop_items', target: 3, description: '让3个宝石掉到底部 💎' }
    ],
    starRequirements: [3500, 6000, 9000]
  },
  
  // 第8关：限时挑战（步数紧张）
  {
    id: 8,
    name: "极速消除",
    description: "在12步内达到4000分",
    moves: 12,
    objectives: [
      { type: 'score', target: 4000, description: '达到4000分' }
    ],
    starRequirements: [4000, 6000, 8500]
  },
  
  // 第9关：多目标挑战
  {
    id: 9,
    name: "全面考验",
    description: "完成所有目标",
    moves: 30,
    objectives: [
      { type: 'score', target: 5000, description: '达到5000分' },
      { type: 'collect', target: 20, targetType: 2, description: '收集20个水滴 💧' },
      { type: 'special', target: 8, description: '使用8个特殊道具' },
      { type: 'combo', target: 4, description: '达成4连击' }
    ],
    starRequirements: [5000, 8000, 12000]
  },
  
  // 第10关：终极挑战
  {
    id: 10,
    name: "霓虹之王",
    description: "证明你是真正的消除大师！",
    moves: 35,
    objectives: [
      { type: 'score', target: 8000, description: '达到8000分' },
      { type: 'collect', target: 30, targetType: 4, description: '收集30个钻石 💎' },
      { type: 'clear_obstacle', target: 12, description: '清除12个冰块' },
      { type: 'combo', target: 6, description: '达成6连击' }
    ],
    starRequirements: [8000, 12000, 18000],
    blockedCells: [
      {row: 1, col: 1}, {row: 1, col: 6},
      {row: 2, col: 2}, {row: 2, col: 5},
      {row: 3, col: 3}, {row: 3, col: 4},
      {row: 4, col: 3}, {row: 4, col: 4},
      {row: 5, col: 2}, {row: 5, col: 5},
      {row: 6, col: 1}, {row: 6, col: 6}
    ]
  }
]

// 获取总关卡数
export const TOTAL_LEVELS = LEVELS.length

// 获取关卡解锁状态（从本地存储）
export function getLevelProgress(): { stars: number[], unlocked: boolean[] } {
  const saved = localStorage.getItem('match3_level_progress')
  if (saved) {
    return JSON.parse(saved)
  }
  
  // 默认：第一关解锁，其他锁定
  const stars = new Array(TOTAL_LEVELS).fill(0)
  const unlocked = new Array(TOTAL_LEVELS).fill(false)
  unlocked[0] = true
  
  return { stars, unlocked }
}

// 保存关卡进度
export function saveLevelProgress(levelId: number, stars: number) {
  const progress = getLevelProgress()
  
  // 更新当前关卡星星数（只保存最高成绩）
  progress.stars[levelId - 1] = Math.max(progress.stars[levelId - 1], stars)
  
  // 解锁下一关
  if (levelId < TOTAL_LEVELS) {
    progress.unlocked[levelId] = true
  }
  
  localStorage.setItem('match3_level_progress', JSON.stringify(progress))
}

// 获取关卡总星星数
export function getTotalStars(): number {
  const progress = getLevelProgress()
  return progress.stars.reduce((sum, s) => sum + s, 0)
}
