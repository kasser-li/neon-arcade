# GIS地理信息系统 - 开发文档

> 技术栈：Vue 3 + Node.js + TypeScript + MongoDB
> 版本：v1.0
> 创建时间：2026-03-19

---

## 一、项目结构

```
gis-system/
├── frontend/                    # 前端项目
│   ├── src/
│   │   ├── api/                 # API接口
│   │   ├── assets/              # 静态资源
│   │   ├── components/          # 组件
│   │   │   ├── common/          # 通用组件
│   │   │   ├── map/             # 地图组件
│   │   │   └── dwg/             # DWG组件
│   │   ├── composables/         # 组合式函数
│   │   ├── router/              # 路由
│   │   ├── stores/              # Pinia状态管理
│   │   ├── styles/              # 样式
│   │   ├── types/               # TypeScript类型
│   │   ├── utils/               # 工具函数
│   │   ├── views/               # 页面视图
│   │   │   ├── login/
│   │   │   ├── project/
│   │   │   ├── map/
│   │   │   └── admin/
│   │   ├── App.vue
│   │   └── main.ts
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── backend/                     # 后端项目
│   ├── src/
│   │   ├── config/              # 配置
│   │   ├── controllers/         # 控制器
│   │   ├── middlewares/         # 中间件
│   │   ├── models/              # 数据模型
│   │   ├── routes/              # 路由
│   │   ├── services/            # 业务逻辑
│   │   ├── types/               # TypeScript类型
│   │   ├── utils/               # 工具函数
│   │   ├── app.ts               # Express应用
│   │   └── index.ts             # 入口
│   ├── uploads/                 # 上传文件
│   ├── package.json
│   ├── tsconfig.json
│   └── docker-compose.yml
│
└── README.md
```

---

## 二、前端开发

### 2.1 环境搭建

```bash
# 创建Vue项目
cd frontend
npm create vue@latest .

# 安装依赖
npm install
npm install vue-router@4 pinia axios element-plus
npm install leaflet @types/leaflet
npm install turf @turf/turf
npm install fabric

# 开发服务器
npm run dev
```

### 2.2 核心组件

#### 2.2.1 地图组件 (MapContainer.vue)
```vue
<template>
  <div ref="mapRef" class="map-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const mapRef = ref<HTMLElement>()
let map: L.Map

onMounted(() => {
  // 初始化地图
  map = L.map(mapRef.value!, {
    center: [39.9042, 116.4074],  // 北京
    zoom: 12,
    zoomControl: false
  })
  
  // 添加底图
  L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
    subdomains: '1234'
  }).addTo(map)
  
  // 添加缩放控件
  L.control.zoom({ position: 'bottomright' }).addTo(map)
})

onUnmounted(() => {
  map?.remove()
})
</script>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
}
</style>
```

#### 2.2.2 DWG预览组件 (DwgViewer.vue)
```vue
<template>
  <div class="dwg-viewer">
    <div ref="svgRef" class="svg-container"></div>
    <layer-control :layers="layers" @toggle="toggleLayer" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as fabric from 'fabric'

const props = defineProps<{
  dwgId: string
}>()

const svgRef = ref<HTMLElement>()
const layers = ref([])
let canvas: fabric.Canvas

onMounted(async () => {
  // 加载DWG解析后的数据
  const dwgData = await fetchDwgData(props.dwgId)
  
  // 使用Fabric.js渲染
  canvas = new fabric.Canvas(svgRef.value, {
    width: 800,
    height: 600
  })
  
  // 渲染图层
  renderLayers(dwgData.layers)
})

function renderLayers(layers: any[]) {
  layers.forEach(layer => {
    layer.entities.forEach((entity: any) => {
      switch(entity.type) {
        case 'line':
          drawLine(entity)
          break
        case 'circle':
          drawCircle(entity)
          break
        case 'text':
          drawText(entity)
          break
      }
    })
  })
}

function drawLine(entity: any) {
  const line = new fabric.Line(
    [entity.start.x, entity.start.y, entity.end.x, entity.end.y],
    { stroke: entity.color || '#000' }
  )
  canvas.add(line)
}
</script>
```

#### 2.2.3 标注组件 (MarkerTool.vue)
```vue
<template>
  <div class="marker-tool">
    <el-button-group>
      <el-button 
        :type="activeTool === 'point' ? 'primary' : ''"
        @click="setTool('point')"
      >
        <el-icon><Location /></el-icon> 标点
      </el-button>
      <el-button 
        :type="activeTool === 'line' ? 'primary' : ''"
        @click="setTool('line')"
      >
        <el-icon><Share /></el-icon> 画线
      </el-button>
      <el-button 
        :type="activeTool === 'polygon' ? 'primary' : ''"
        @click="setTool('polygon')"
      >
        <el-icon><FullScreen /></el-icon> 画面
      </el-button>
    </el-button-group>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Location, Share, FullScreen } from '@element-plus/icons-vue'

const activeTool = ref('')
const emit = defineEmits(['toolChange'])

function setTool(tool: string) {
  activeTool.value = tool
  emit('toolChange', tool)
}
</script>
```

### 2.3 状态管理 (Pinia)

```typescript
// stores/map.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Marker, Layer } from '@/types'

export const useMapStore = defineStore('map', () => {
  // State
  const markers = ref<Marker[]>([])
  const layers = ref<Layer[]>([])
  const selectedMarker = ref<Marker | null>(null)
  const activeTool = ref('select')
  
  // Getters
  const visibleMarkers = computed(() => 
    markers.value.filter(m => m.visible && m.status === 'active')
  )
  
  const markerCount = computed(() => markers.value.length)
  
  // Actions
  function addMarker(marker: Marker) {
    markers.value.push(marker)
  }
  
  function updateMarker(id: string, data: Partial<Marker>) {
    const index = markers.value.findIndex(m => m.id === id)
    if (index > -1) {
      markers.value[index] = { ...markers.value[index], ...data }
    }
  }
  
  function deleteMarker(id: string) {
    const index = markers.value.findIndex(m => m.id === id)
    if (index > -1) {
      markers.value.splice(index, 1)
    }
  }
  
  function setActiveTool(tool: string) {
    activeTool.value = tool
  }
  
  return {
    markers,
    layers,
    selectedMarker,
    activeTool,
    visibleMarkers,
    markerCount,
    addMarker,
    updateMarker,
    deleteMarker,
    setActiveTool
  }
})
```

### 2.4 API封装

```typescript
// api/marker.ts
import axios from 'axios'
import type { Marker, MarkerQuery } from '@/types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000
})

export const markerApi = {
  // 创建标点
  create(data: Partial<Marker>) {
    return api.post<Marker>('/api/markers', data)
  },
  
  // 查询标点
  query(params: MarkerQuery) {
    return api.get<{ list: Marker[]; total: number }>('/api/markers', { params })
  },
  
  // 更新标点
  update(id: string, data: Partial<Marker>) {
    return api.put<Marker>(`/api/markers/${id}`, data)
  },
  
  // 删除标点
  delete(id: string) {
    return api.delete(`/api/markers/${id}`)
  },
  
  // 批量导入
  import(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/api/markers/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  // 导出
  export(params: MarkerQuery) {
    return api.get('/api/markers/export', { 
      params,
      responseType: 'blob'
    })
  }
}
```

---

## 三、后端开发

### 3.1 环境搭建

```bash
cd backend
npm init -y
npm install express mongoose cors helmet morgan
npm install -D typescript @types/express @types/node ts-node nodemon
npm install multer sharp
npm install jsonwebtoken bcryptjs
npm install winston                    # 日志
npm install ioredis                    # Redis
npm install @aws-sdk/client-s3         # MinIO兼容S3

# 初始化TypeScript
npx tsc --init
```

### 3.2 项目配置

```typescript
// src/config/index.ts
export const config = {
  port: process.env.PORT || 3000,
  mongoUri: process.env.MONGO_URI || 'mongodb://localhost:27017/gis_system',
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379',
  jwtSecret: process.env.JWT_SECRET || 'your-secret-key',
  uploadDir: process.env.UPLOAD_DIR || './uploads',
  maxFileSize: 100 * 1024 * 1024  // 100MB
}
```

### 3.3 Express应用

```typescript
// src/app.ts
import express from 'express'
import cors from 'cors'
import helmet from 'helmet'
import morgan from 'morgan'
import { connectDB } from './config/database'
import { errorHandler } from './middlewares/errorHandler'
import { authRouter } from './routes/auth'
import { projectRouter } from './routes/project'
import { dwgRouter } from './routes/dwg'
import { markerRouter } from './routes/marker'

const app = express()

// 中间件
app.use(helmet())
app.use(cors())
app.use(morgan('dev'))
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

// 路由
app.use('/api/auth', authRouter)
app.use('/api/projects', projectRouter)
app.use('/api/dwg', dwgRouter)
app.use('/api/markers', markerRouter)

// 静态文件
app.use('/uploads', express.static('uploads'))

// 错误处理
app.use(errorHandler)

// 连接数据库
connectDB()

export { app }
```

### 3.4 MongoDB模型

```typescript
// src/models/Marker.ts
import mongoose, { Schema, Document } from 'mongoose'

export interface IMarker extends Document {
  projectId: mongoose.Types.ObjectId
  name: string
  type: string
  description?: string
  coordinates: { lng: number; lat: number }
  properties: Record<string, any>
  creator: mongoose.Types.ObjectId
  status: string
  createTime: Date
  updateTime: Date
}

const MarkerSchema = new Schema<IMarker>({
  projectId: { type: Schema.Types.ObjectId, ref: 'Project', required: true },
  name: { type: String, required: true },
  type: { type: String, default: 'normal' },
  description: String,
  coordinates: {
    lng: { type: Number, required: true },
    lat: { type: Number, required: true }
  },
  properties: { type: Schema.Types.Mixed, default: {} },
  creator: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  status: { type: String, enum: ['active', 'inactive', 'deleted'], default: 'active' },
  createTime: { type: Date, default: Date.now },
  updateTime: { type: Date, default: Date.now }
})

// 地理空间索引
MarkerSchema.index({ coordinates: '2dsphere' })
MarkerSchema.index({ projectId: 1, status: 1 })

export const Marker = mongoose.model<IMarker>('Marker', MarkerSchema)
```

```typescript
// src/models/DwgFile.ts
import mongoose, { Schema, Document } from 'mongoose'

export interface IDwgFile extends Document {
  projectId: mongoose.Types.ObjectId
  name: string
  originalName: string
  size: number
  status: 'pending' | 'parsing' | 'parsed' | 'error'
  layers: Array<{
    name: string
    visible: boolean
    color: string
    type: string
  }>
  filePath: string
  geojsonPath?: string
  creator: mongoose.Types.ObjectId
  createTime: Date
}

const DwgFileSchema = new Schema<IDwgFile>({
  projectId: { type: Schema.Types.ObjectId, ref: 'Project', required: true },
  name: { type: String, required: true },
  originalName: { type: String, required: true },
  size: { type: Number, required: true },
  status: { 
    type: String, 
    enum: ['pending', 'parsing', 'parsed', 'error'],
    default: 'pending'
  },
  layers: [{
    name: String,
    visible: { type: Boolean, default: true },
    color: String,
    type: String
  }],
  filePath: { type: String, required: true },
  geojsonPath: String,
  creator: { type: Schema.Types.ObjectId, ref: 'User', required: true },
  createTime: { type: Date, default: Date.now }
})

export const DwgFile = mongoose.model<IDwgFile>('DwgFile', DwgFileSchema)
```

### 3.5 DWG解析服务

```typescript
// src/services/dwgParser.ts
import { spawn } from 'child_process'
import path from 'path'
import fs from 'fs/promises'

export interface DwgParseResult {
  success: boolean
  layers: Array<{
    name: string
    entities: any[]
  }>
  bounds: {
    minX: number
    minY: number
    maxX: number
    maxY: number
  }
  error?: string
}

export class DwgParserService {
  // 使用Python库解析DWG
  async parseWithPython(filePath: string): Promise<DwgParseResult> {
    return new Promise((resolve, reject) => {
      const scriptPath = path.join(__dirname, '../../scripts/parse_dwg.py')
      const process = spawn('python3', [scriptPath, filePath])
      
      let output = ''
      let error = ''
      
      process.stdout.on('data', (data) => {
        output += data.toString()
      })
      
      process.stderr.on('data', (data) => {
        error += data.toString()
      })
      
      process.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`DWG解析失败: ${error}`))
        } else {
          try {
            const result = JSON.parse(output)
            resolve(result)
          } catch (e) {
            reject(new Error('解析结果格式错误'))
          }
        }
      })
    })
  }
  
  // 转换为GeoJSON
  async convertToGeoJSON(dwgData: any): Promise<any> {
    const features = []
    
    dwgData.layers.forEach((layer: any) => {
      layer.entities.forEach((entity: any) => {
        const feature = this.entityToFeature(entity)
        if (feature) features.push(feature)
      })
    })
    
    return {
      type: 'FeatureCollection',
      features
    }
  }
  
  private entityToFeature(entity: any): any | null {
    switch(entity.type) {
      case 'LINE':
        return {
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: [
              [entity.start.x, entity.start.y],
              [entity.end.x, entity.end.y]
            ]
          },
          properties: { color: entity.color }
        }
      case 'CIRCLE':
        // 转换为多边形近似
        return {
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [entity.center.x, entity.center.y]
          },
          properties: { 
            radius: entity.radius,
            color: entity.color 
          }
        }
      case 'TEXT':
        return {
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [entity.position.x, entity.position.y]
          },
          properties: { 
            text: entity.text,
            color: entity.color,
            height: entity.height
          }
        }
      default:
        return null
    }
  }
}

export const dwgParserService = new DwgParserService()
```

### 3.6 DWG解析Python脚本

```python
# scripts/parse_dwg.py
#!/usr/bin/env python3
import sys
import json
import ezdxf

def parse_dwg(file_path):
    try:
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()
        
        layers = {}
        bounds = {
            'minX': float('inf'),
            'minY': float('inf'),
            'maxX': float('-inf'),
            'maxY': float('-inf')
        }
        
        for entity in msp:
            layer_name = entity.dxf.layer
            if layer_name not in layers:
                layers[layer_name] = {
                    'name': layer_name,
                    'entities': []
                }
            
            entity_data = parse_entity(entity)
            if entity_data:
                layers[layer_name]['entities'].append(entity_data)
                update_bounds(entity_data, bounds)
        
        return {
            'success': True,
            'layers': list(layers.values()),
            'bounds': bounds
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def parse