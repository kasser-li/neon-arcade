# GIS地理信息系统 - 开发文档（完整版）

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
│   ├── scripts/                 # Python脚本
│   │   └── parse_dwg.py         # DWG解析
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

#### MapContainer.vue - 地图容器
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
  map = L.map(mapRef.value!, {
    center: [39.9042, 116.4074],
    zoom: 12,
    zoomControl: false
  })
  
  L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
    subdomains: '1234'
  }).addTo(map)
  
  L.control.zoom({ position: 'bottomright' }).addTo(map)
})

onUnmounted(() => {
  map?.remove()
})
</script>

<style scoped>
.map-container { width: 100%; height: 100%; }
</style>
```

#### DwgViewer.vue - DWG预览
```vue
<template>
  <div class="dwg-viewer">
    <div ref="canvasRef" class="canvas-container"></div>
    <layer-control :layers="layers" @toggle="toggleLayer" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as fabric from 'fabric'

const props = defineProps<{ dwgId: string }>()
const canvasRef = ref<HTMLElement>()
const layers = ref([])
let canvas: fabric.Canvas

onMounted(async () => {
  const dwgData = await fetch(`/api/dwg/${props.dwgId}/preview`).then(r => r.json())
  canvas = new fabric.Canvas(canvasRef.value)
  renderDwg(dwgData)
})

function renderDwg(data: any) {
  data.layers.forEach((layer: any) => {
    layer.entities.forEach((entity: any) => {
      if (entity.type === 'LINE') {
        const line = new fabric.Line(
          [entity.start.x, entity.start.y, entity.end.x, entity.end.y],
          { stroke: entity.color || '#000' }
        )
        canvas.add(line)
      }
    })
  })
}
</script>
```

### 2.3 状态管理

```typescript
// stores/map.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useMapStore = defineStore('map', () => {
  const markers = ref([])
  const selectedMarker = ref(null)
  const activeTool = ref('select')
  
  const visibleMarkers = computed(() => 
    markers.value.filter(m => m.visible && m.status === 'active')
  )
  
  function addMarker(marker: any) {
    markers.value.push(marker)
  }
  
  function updateMarker(id: string, data: any) {
    const index = markers.value.findIndex(m => m.id === id)
    if (index > -1) {
      markers.value[index] = { ...markers.value[index], ...data }
    }
  }
  
  return { markers, selectedMarker, activeTool, visibleMarkers, addMarker, updateMarker }
})
```

---

## 三、后端开发

### 3.1 环境搭建

```bash
cd backend
npm init -y
npm install express mongoose cors helmet morgan
npm install -D typescript @types/express @types/node ts-node nodemon
npm install multer
npm install jsonwebtoken bcryptjs
npm install winston ioredis

npx tsc --init
```

### 3.2 Express应用

```typescript
// src/app.ts
import express from 'express'
import cors from 'cors'
import helmet from 'helmet'
import mongoose from 'mongoose'

const app = express()

app.use(helmet())
app.use(cors())
app.use(express.json())

// 路由
app.use('/api/projects', projectRouter)
app.use('/api/dwg', dwgRouter)
app.use('/api/markers', markerRouter)

// 连接MongoDB
mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/gis_system')

export { app }
```

### 3.3 MongoDB模型

```typescript
// src/models/Marker.ts
import mongoose, { Schema } from 'mongoose'

const MarkerSchema = new Schema({
  projectId: { type: Schema.Types.ObjectId, ref: 'Project', required: true },
  name: { type: String, required: true },
  type: { type: String, default: 'normal' },
  coordinates: {
    lng: { type: Number, required: true },
    lat: { type: Number, required: true }
  },
  properties: { type: Schema.Types.Mixed, default: {} },
  creator: { type: Schema.Types.ObjectId, ref: 'User' },
  status: { type: String, enum: ['active', 'deleted'], default: 'active' }
}, { timestamps: true })

MarkerSchema.index({ coordinates: '2dsphere' })
MarkerSchema.index({ projectId: 1, status: 1 })

export const Marker = mongoose.model('Marker', MarkerSchema)
```

```typescript
// src/models/DwgFile.ts
import mongoose, { Schema } from 'mongoose'

const DwgFileSchema = new Schema({
  projectId: { type: Schema.Types.ObjectId, ref: 'Project', required: true },
  name: String,
  originalName: String,
  size: Number,
  status: { type: String, enum: ['pending', 'parsed', 'error'], default: 'pending' },
  layers: [{ name: String, visible: Boolean, color: String, type: String }],
  filePath: String,
  geojsonPath: String
}, { timestamps: true })

export const DwgFile = mongoose.model('DwgFile', DwgFileSchema)
```

### 3.4 DWG解析服务

```typescript
// src/services/dwgParser.ts
import { spawn } from 'child_process'
import path from 'path'

export class DwgParserService {
  async parse(filePath: string): Promise<any> {
    return new Promise((resolve, reject) => {
      const script = path.join(__dirname, '../../scripts/parse_dwg.py')
      const proc = spawn('python3', [script, filePath])
      
      let output = '', error = ''
      proc.stdout.on('data', (data) => output += data)
      proc.stderr.on('data', (data) => error += data)
      
      proc.on('close', (code) => {
        if (code !== 0) reject(new Error(error))
        else resolve(JSON.parse(output))
      })
    })
  }
}

export const dwgParser = new DwgParserService()
```

### 3.5 Python解析脚本

```python
# scripts/parse_dwg.py
#!/usr/bin/env python3
import sys
import json

try:
    import ezdxf
except ImportError:
    print(json.dumps({'success': False, 'error': '缺少ezdxf库，请运行: pip install ezdxf'}))
    sys.exit(1)

def parse_entity(entity):
    t = entity.dxftype()
    if t == 'LINE':
        return {
            'type': 'LINE',
            'start': {'x': entity.dxf.start.x, 'y': entity.dxf.start.y},
            'end': {'x': entity.dxf.end.x, 'y': entity.dxf.end.y},
            'color': entity.dxf.color
        }
    elif t == 'CIRCLE':
        return {
            'type': 'CIRCLE',
            'center': {'x': entity.dxf.center.x, 'y': entity.dxf.center.y},
            'radius': entity.dxf.radius,
            'color': entity.dxf.color
        }
    elif t == 'TEXT':
        return {
            'type': 'TEXT',
            'position': {'x': entity.dxf.insert.x, 'y': entity.dxf.insert.y},
            'text': entity.dxf.text,
            'height': entity.dxf.height,
            'color': entity.dxf.color
        }
    elif t == 'LWPOLYLINE':
        return {
            'type': 'LWPOLYLINE',
            'points': [{'x': p[0], 'y': p[1]} for p in entity.get_points()],
            'is_closed': entity.closed,
            'color': entity.dxf.color
        }
    return None

def parse_dwg(file_path):
    try:
        doc = ezdxf.readfile(file_path)
        msp = doc.modelspace()
        
        layers = {}
        bounds = {'minX': float('inf'), 'minY': float('inf'), 'maxX': float('-inf'), 'maxY': float('-inf')}
        
        for entity in msp:
            layer_name = entity.dxf.layer
            if layer_name not in layers:
                layers[layer_name] = {'name': layer_name, 'entities': []}
            
            data = parse_entity(entity)
            if data:
                layers[layer_name]['entities'].append(data)
                # 更新边界
                if 'start' in data:
                    bounds['minX'] = min(bounds['minX'], data['start']['x'])
                    bounds['minY'] = min(bounds['minY'], data['start']['y'])
                    bounds['maxX'] = max(bounds['maxX'], data['start']['x'])
                    bounds['maxY'] = max(bounds['maxY'], data['start']['y'])
        
        return {'success': True, 'layers': list(layers.values()), 'bounds': bounds}
    except Exception as e:
        return {'success': False, 'error': str(e)}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'success': False, 'error': '缺少文件路径'}))
        sys.exit(1)
    
    result = parse_dwg(sys.argv[1])
    print(json.dumps(result))
```

### 3.6 控制器

```typescript
// src/controllers/markerController.ts
import { Request, Response } from 'express'
import { Marker } from '../models/Marker'

export const markerController = {
  async create(req: Request, res: Response) {
    try {
      const marker = await Marker.create({ ...req.body, creator: req.user?.id })
      res.status(201).json(marker)
    } catch (error: any) {
      res.status(400).json({ error: error.message })
    }
  },

  async query(req: Request, res: Response) {
    try {
      const { projectId, page = 1, pageSize = 100 } = req.query
      const filter: any = { projectId, status: 'active' }
      
      const [list, total] = await Promise.all([
        Marker.find(filter)
          .skip((Number(page) - 1) * Number(pageSize))
          .limit(Number(pageSize))
          .sort({ createdAt: -1 }),
        Marker.countDocuments(filter)
      ])
      
      res.json({ list, total, page: Number(page), pageSize: Number(pageSize) })
    } catch (error: any) {
      res.status(500).json({ error: error.message })
    }
  },

  async update(req: Request, res: Response) {
    try {
      const marker = await Marker.findByIdAndUpdate(
        req.params.id,
        req.body,
        { new: true }
      )
      res.json(marker)
    } catch (error: any) {
      res.status(400).json({ error: error.message })
    }
  },

  async delete(req: Request, res: Response) {
    try {
      await Marker.findByIdAndUpdate(req.params.id, { status: 'deleted' })
      res.json({ success: true })
    } catch (error: any) {
      res.status(500).json({ error: error.message })
    }
  }
}
```

### 3.7 路由

```typescript
// src/routes/marker.ts
import { Router } from 'express'
import { markerController } from '../controllers/markerController'

const router = Router()

router.post('/', markerController.create)
router.get('/', markerController.query)
router.put('/:id', markerController.update)
router.delete('/:id', markerController.delete)

export { router as markerRouter }
```

---

## 四、部署

### 4.1 Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - MONGO_URI=mongodb://mongo:27017/gis_system
    depends_on:
      - mongo
  
  mongo:
    image: mongo:7
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./frontend/dist:/usr/share/nginx/html

volumes:
  mongo_data:
```

### 4.2 Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app

# 安装Python
RUN apk add --no-cache python3 py3-pip
RUN pip3 install ezdxf

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["node", "dist/index.js"]
```

---

## 五、开发命令

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建
npm run build

# 生产运行
npm start

# Docker
docker-compose up -d
```

---

*文档创建：2026-03-19*
*技术栈：Vue 3 + Node.js + TypeScript + MongoDB*
