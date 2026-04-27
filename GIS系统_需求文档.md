# GIS地理信息系统 - 需求文档

> 版本：v1.0
> 创建时间：2026-03-19
> 技术栈：Vue 3 + Node.js + TypeScript + MongoDB

---

## 一、项目概述

### 1.1 项目背景
开发一套基于Web的GIS地理信息系统，支持DWG图纸解析、地图标注、信息管理等功能，满足工程图纸在线浏览和标注需求。

### 1.2 项目目标
- 实现DWG文件的在线解析和展示
- 提供地图标注和标点功能
- 支持标点信息的增删改查
- 实现用户权限管理

### 1.3 技术选型
| 层级 | 技术 | 版本 |
|------|------|------|
| 前端 | Vue 3 + TypeScript | ^3.4.0 |
| 前端UI | Element Plus | ^2.5.0 |
| GIS引擎 | Leaflet / OpenLayers | ^1.9.0 |
| DWG解析 | @cadjs/dwg-parser / 后端转换 | - |
| 后端 | Node.js + Express + TypeScript | ^20.0.0 |
| 数据库 | MongoDB | ^7.0 |
| 缓存 | Redis | ^7.0 |
| 文件存储 | MinIO / 本地 | - |

---

## 二、功能需求

### 2.1 DWG文件管理

#### 2.1.1 DWG文件上传
**功能描述**：支持用户上传DWG格式的CAD图纸文件

**核心功能**：
- 单文件/批量上传
- 文件格式校验（.dwg, .dxf）
- 上传进度显示
- 文件大小限制（最大100MB）
- 文件元数据提取（文件名、版本、创建时间等）

**验收标准**：
- 支持AutoCAD 2004-2024版本的DWG文件
- 上传进度实时显示
- 上传失败有明确错误提示

#### 2.1.2 DWG文件解析
**功能描述**：将DWG文件解析为Web可展示的格式

**核心功能**：
- DWG文件格式转换（转为GeoJSON/SVG/PNG）
- 图层信息提取
- 坐标系统识别和转换
- 解析进度显示
- 解析结果预览

**验收标准**：
- 支持常见图层类型（点、线、面、文字）
- 坐标精度保持
- 解析时间 < 30秒（50MB文件）
- 支持中文显示

#### 2.1.3 DWG文件浏览
**功能描述**：在Web端浏览解析后的DWG图纸

**核心功能**：
- 矢量图形渲染
- 图层控制（显示/隐藏）
- 缩放、平移、旋转
- 测量工具（距离、面积）
- 全屏查看
- 缩略图导航

**验收标准**：
- 缩放流畅（60fps）
- 支持10万+图形元素
- 响应式布局适配

### 2.2 地图标注功能

#### 2.2.1 标点功能
**功能描述**：在地图上添加标注点

**核心功能**：
- 点击地图添加标点
- 支持多种标点图标（自定义图标库）
- 标点拖拽移动
- 标点删除
- 批量导入标点（Excel/CSV）
- 标点分组管理

**标点类型**：
| 类型 | 图标 | 用途 |
|------|------|------|
| 普通点 | 🔵 | 一般标注 |
| 重要点 | 🔴 | 关键位置 |
| 监测点 | 📊 | 数据监测 |
| 设备点 | ⚙️ | 设备位置 |
| 危险点 | ⚠️ | 危险区域 |

**验收标准**：
- 标点位置精度 < 1米
- 支持同时显示1000+标点
- 标点击中率 > 95%

#### 2.2.2 标注线/面
**功能描述**：在地图上绘制线和多边形

**核心功能**：
- 绘制折线
- 绘制多边形
- 绘制圆形
- 绘制矩形
- 编辑节点
- 删除图形

**验收标准**：
- 绘制流畅无卡顿
- 支持撤销/重做
- 节点编辑精准

#### 2.2.3 标注样式
**功能描述**：自定义标注的样式

**核心功能**：
- 图标选择
- 颜色设置
- 大小调整
- 透明度设置
- 标签文字样式
- 悬停效果

### 2.3 标点信息管理

#### 2.3.1 信息录入
**功能描述**：为标点添加详细信息

**核心字段**：
```typescript
interface MarkerInfo {
  id: string;                    // 唯一标识
  name: string;                  // 标点名称
  type: MarkerType;              // 标点类型
  description?: string;          // 描述
  coordinates: [number, number]; // 坐标 [lng, lat]
  altitude?: number;             // 海拔
  
  // 扩展信息
  properties: {
    [key: string]: any;          // 自定义属性
  };
  
  // 媒体信息
  images?: string[];             // 图片
  videos?: string[];             // 视频
  documents?: string[];          // 文档
  
  // 元数据
  creator: string;               // 创建人
  createTime: Date;              // 创建时间
  updater?: string;              // 更新人
  updateTime?: Date;             // 更新时间
  
  // 状态
  status: 'active' | 'inactive' | 'deleted';
}
```

**验收标准**：
- 支持富文本描述
- 支持多图片上传
- 字段验证完整

#### 2.3.2 信息查询
**功能描述**：查询和检索标点信息

**核心功能**：
- 按名称搜索
- 按类型筛选
- 按时间范围筛选
- 按属性筛选
- 空间查询（框选、圆形选）
- 组合查询

**验收标准**：
- 搜索结果 < 1秒
- 支持分页（100条/页）
- 支持排序

#### 2.3.3 信息编辑
**功能描述**：修改标点信息

**核心功能**：
- 在线编辑
- 批量编辑
- 历史版本
- 变更记录
- 数据校验

#### 2.3.4 信息导出
**功能描述**：导出标点数据

**导出格式**：
- Excel (.xlsx)
- CSV
- GeoJSON
- KML/KMZ
- Shapefile

### 2.4 图层管理

#### 2.4.1 图层控制
**功能描述**：管理DWG图层和标注图层

**核心功能**：
- 图层显示/隐藏
- 图层透明度调整
- 图层顺序调整
- 图层锁定
- 图层组管理

#### 2.4.2 底图切换
**功能描述**：切换不同的地图底图

**支持底图**：
- 高德地图
- 百度地图
- 天地图
- OpenStreetMap
- 卫星影像
- 自定义瓦片

### 2.5 用户与权限

#### 2.5.1 用户管理
- 用户注册/登录
- 用户角色（管理员、编辑者、查看者）
- 个人中心

#### 2.5.2 权限控制
- 项目级权限
- 图层级权限
- 操作权限（查看、编辑、删除）

### 2.6 项目管理

#### 2.6.1 项目创建
- 项目名称、描述
- 坐标系统设置
- 成员管理

#### 2.6.2 项目设置
- 默认底图
- 默认样式
- 导出模板

---

## 三、非功能需求

### 3.1 性能需求
| 指标 | 要求 |
|------|------|
| 页面加载 | < 3秒 |
| DWG解析 | < 30秒（50MB） |
| 地图渲染 | 60fps |
| 标点查询 | < 1秒 |
| 并发用户 | 支持100+ |

### 3.2 兼容性需求
- Chrome 90+
- Firefox 90+
- Safari 15+
- Edge 90+
- 移动端适配

### 3.3 安全需求
- JWT认证
- 接口权限控制
- 文件上传安全校验
- 数据加密存储

---

## 四、界面原型

### 4.1 主界面布局
```
┌─────────────────────────────────────────────────┐
│  顶部导航栏（Logo、项目选择、用户菜单）            │
├──────────┬──────────────────────────┬──────────┤
│          │                          │          │
│  图层    │                          │  属性    │
│  面板    │      地图区域             │  面板    │
│  (左)    │                          │  (右)    │
│          │                          │          │
├──────────┴──────────────────────────┴──────────┤
│  底部状态栏（坐标、比例尺、当前操作）             │
└─────────────────────────────────────────────────┘
```

### 4.2 工具栏
- 选择工具
- 标点工具
- 画线工具
- 画面工具
- 测量工具
- 全屏
- 缩放控制

---

## 五、接口概览

### 5.1 DWG接口
```
POST   /api/dwg/upload        上传DWG
GET    /api/dwg/:id           获取DWG信息
GET    /api/dwg/:id/preview   预览DWG
DELETE /api/dwg/:id           删除DWG
POST   /api/dwg/:id/parse     解析DWG
GET    /api/dwg/:id/layers    获取图层列表
```

### 5.2 标注接口
```
POST   /api/markers           创建标点
GET    /api/markers           查询标点
PUT    /api/markers/:id       更新标点
DELETE /api/markers/:id       删除标点
POST   /api/markers/batch     批量操作
POST   /api/markers/import    导入标点
GET    /api/markers/export    导出标点
```

### 5.3 项目接口
```
POST   /api/projects          创建项目
GET    /api/projects          项目列表
GET    /api/projects/:id      项目详情
PUT    /api/projects/:id      更新项目
DELETE /api/projects/:id      删除项目
```

---

## 六、数据库设计

### 6.1 集合结构

#### projects（项目）
```javascript
{
  _id: ObjectId,
  name: String,
  description: String,
  coordinateSystem: String,  // 坐标系
  defaultBaseMap: String,    // 默认底图
  creator: ObjectId,
  members: [{
    userId: ObjectId,
    role: String,            // admin/editor/viewer
    joinTime: Date
  }],
  createTime: Date,
  updateTime: Date
}
```

#### dwgFiles（DWG文件）
```javascript
{
  _id: ObjectId,
  projectId: ObjectId,
  name: String,
  originalName: String,
  size: Number,
  version: String,           // DWG版本
  status: String,            // pending/parsed/error
  layers: [{
    name: String,
    visible: Boolean,
    color: String,
    type: String             // point/line/polygon/text
  }],
  bounds: {
    minX: Number,
    minY: Number,
    maxX: Number,
    maxY: Number
  },
  filePath: String,          // 存储路径
  previewPath: String,       // 预览图路径
  geojsonPath: String,       // 转换后的GeoJSON
  creator: ObjectId,
  createTime: Date,
  parseTime: Date
}
```

#### markers（标注点）
```javascript
{
  _id: ObjectId,
  projectId: ObjectId,
  dwgFileId: ObjectId,       // 关联的DWG（可选）
  name: String,
  type: String,              // normal/important/monitor/device/danger
  description: String,
  coordinates: {
    lng: Number,
    lat: Number
  },
  altitude: Number,
  properties: Object,        // 自定义属性
  style: {
    icon: String,
    color: String,
    size: Number,
    label: String
  },
  images: [String],
  videos: [String],
  documents: [String],
  creator: ObjectId,
  createTime: Date,
  updater: ObjectId,
  updateTime: Date,
  status: String             // active/inactive/deleted
}
```

---

## 七、项目里程碑

| 阶段 | 时间 | 交付物 |
|------|------|--------|
| 需求分析 | Week 1 | 需求文档 |
| 技术设计 | Week 2 | 技术方案、数据库设计 |
| 基础开发 | Week 3-4 | 项目框架、基础功能 |
| DWG模块 | Week 5-6 | 上传、解析、浏览 |
| 标注模块 | Week 7-8 | 标点、画线、信息管理 |
| 优化测试 | Week 9 | 性能优化、Bug修复 |
| 上线部署 | Week 10 | 生产环境部署 |

---

*文档创建：2026-03-19*
*维护人：产品团队*
