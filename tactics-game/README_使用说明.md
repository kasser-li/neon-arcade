# Blender 骑士建模 - 使用说明

## 📦 第一步：安装 Blender

### 下载地址
- 官网：https://www.blender.org/download/
- 中文版：https://www.blender.org/download/ （自动检测语言）

### 版本要求
- **最低版本**：Blender 3.0+
- **推荐版本**：Blender 4.0+（最新 LTS）

### 安装步骤
1. 下载对应系统的安装包
2. 双击安装（Windows）或拖拽到应用程序（Mac）
3. 启动 Blender

---

## 🚀 第二步：运行脚本

### 方法一：直接运行（推荐）

1. 打开 Blender
2. 删除默认立方体（选中后按 `X` 或 `Delete`）
3. 点击顶部菜单栏 **Scripting**（脚本编辑）
4. 点击 **Open**（打开）按钮
5. 选择 `blender_knight.py` 文件
6. 点击 **▶ Run Script**（运行脚本）按钮

### 方法二：文本编辑器运行

1. 打开 Blender
2. 按 `Shift + F11` 打开文本编辑器
3. 点击 **Open** 按钮，选择 `blender_knight.py`
4. 点击编辑器右上角的 **▶** 播放按钮

### 方法三：命令行运行（批量处理）

```bash
# Windows
blender --background --python blender_knight.py

# Mac
/Applications/Blender.app/Contents/MacOS/Blender --background --python blender_knight.py

# Linux
blender --background --python blender_knight.py
```

---

## 🎨 第三步：查看和调整

### 查看模型
- **旋转视角**：鼠标中键拖拽
- **平移视角**：`Shift +` 鼠标中键拖拽
- **缩放视角**：鼠标滚轮
- **聚焦选中物体**：按 `.`（小键盘）或 `Shift + C`

### 调整材质
1. 选中物体
2. 切换到 **Shading** 工作区
3. 调整材质节点参数

### 调整模型
1. 选中物体
2. 按 `Tab` 进入编辑模式
3. 选择顶点/边/面进行调整
4. 按 `Tab` 退出编辑模式

---

## 💾 第四步：导出模型

### 导出为 GLB/GLTF（推荐用于 Three.js）

1. 点击 **File** > **Export** > **glTF 2.0 (.glb/.gltf)**
2. 选择保存位置
3. 格式选择 **glTF Binary (.glb)**
4. 勾选以下选项：
   - ✅ Apply Modifiers
   - ✅ UVs
   - ✅ Normals
   - ✅ Tangents
5. 点击 **Export glTF 2.0**

### 导出为 OBJ（通用格式）

1. 点击 **File** > **Export** > **Wavefront (.obj)**
2. 勾选 **Include > Selection Only**（仅导出选中的）
3. 点击 **Export OBJ**

---

## 🎬 第五步：渲染（可选）

### 快速预览
1. 按 `Z` 键选择渲染模式
   - **Wireframe**：线框模式
   - **Solid**：实体模式
   - **Material Preview**：材质预览
   - **Rendered**：渲染预览

### 正式渲染
1. 按 `F12` 渲染当前帧
2. 渲染完成后，点击 **Image** > **Save As** 保存图片

### 调整渲染设置
1. 切换到 **Render Properties**（右侧渲染图标）
2. 调整以下参数：
   - **Samples**：采样数（越高越清晰，默认 128）
   - **Resolution**：分辨率（默认 1920×1080）

---

## 🔧 常见问题

### Q: 脚本运行报错怎么办？
A: 检查 Blender 版本，确保是 3.0+。如果还有问题，打开 Blender 的系统控制台查看详细错误信息。

### Q: 模型比例不对？
A: 选中模型，按 `S` 缩放，或进入编辑模式调整顶点位置。

### Q: 材质颜色不对？
A: 选中物体，切换到 **Shading** 工作区，调整 Principled BSDF 节点的 Base Color。

### Q: 如何添加动画？
A: 
1. 切换到 **Animation** 工作区
2. 选中物体，按 `I` 插入关键帧
3. 移动时间轴，调整物体位置，再按 `I` 插入关键帧
4. 按空格键播放动画

### Q: 如何导出到 Three.js 使用？
A: 
1. 导出为 .glb 格式
2. 在 Three.js 中使用 GLTFLoader 加载：

```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const loader = new GLTFLoader();
loader.load('knight.glb', (gltf) => {
    scene.add(gltf.scene);
});
```

---

## 📁 文件说明

| 文件名 | 说明 |
|--------|------|
| `blender_knight.py` | Blender Python 建模脚本 |
| `README_使用说明.md` | 本说明文档 |
| `knight-final-v2.html` | Three.js 直接查看版本（参考） |

---

## 🎯 快捷操作

| 快捷键 | 功能 |
|--------|------|
| `G` | 移动物体 |
| `R` | 旋转物体 |
| `S` | 缩放物体 |
| `X` / `Delete` | 删除物体 |
| `Tab` | 切换编辑/物体模式 |
| `Z` | 切换渲染模式 |
| `F12` | 渲染 |
| `Shift + A` | 添加物体 |
| `Ctrl + Z` | 撤销 |
| `Ctrl + Shift + Z` | 重做 |

---

**祝你建模愉快！🛡️**
