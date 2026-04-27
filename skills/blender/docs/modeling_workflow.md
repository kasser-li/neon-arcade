# Blender 角色建模工作流

## 📋 完整流程

```
1. 准备阶段 → 2. 基础形体 → 3. 细化建模 → 4. 材质纹理 → 5. 灯光渲染 → 6. 导出
```

---

## 1️⃣ 准备阶段

### 导入三视图参考

```python
import bpy

# 加载前视图
bpy.ops.image.open(filepath="/path/to/front_view.png")
# 在正交视图中设置为背景

# 加载侧视图
bpy.ops.image.open(filepath="/path/to/side_view.png")

# 加载顶视图
bpy.ops.image.open(filepath="/path/to/top_view.png")
```

### 手动设置（推荐）

1. 按 `N` 打开侧边栏
2. 找到 **View** → **Background Images**
3. 点击 **Add Image**
4. 选择三视图文件
5. 设置不透明度（0.3-0.5）
6. 在前/侧/顶视图中分别对齐

---

## 2️⃣ 基础形体（Blocking）

### 身体比例

```python
# 头部（球体）
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(0, 0, 1.7))

# 躯干（圆柱体）
bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.5, location=(0, 0, 1.2))

# 骨盆（立方体）
bpy.ops.mesh.primitive_cube_add(size=0.35, location=(0, 0, 0.9))

# 大腿（圆柱体 ×2）
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.45, location=(-0.1, 0, 0.45))
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.45, location=(0.1, 0, 0.45))

# 小腿（圆柱体 ×2）
bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.45, location=(-0.1, 0, 0))
bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.45, location=(0.1, 0, 0))
```

### 比例检查清单

- [ ] 头身比正确（写实 7.5 头身，Q 版 2-3 头身）
- [ ] 肩宽约 2 个头宽
- [ ] 腿长约占身高 1/2
- [ ] 手臂长度（指尖到大腿中部）
- [ ] 左右对称

---

## 3️⃣ 细化建模

### 添加细节

```python
# 使用细分表面修改器
bpy.ops.object.modifier_add(type='SUBSURF')
bpy.context.object.modifiers["Subdivision"].levels = 2
bpy.context.object.modifiers["Subdivision"].render_levels = 3

# 添加边缘环保持形状
bpy.ops.mesh.loopcut_slide(control=1, offset=0.5)

# 倒角边缘
bpy.ops.mesh.bevel(offset=0.02, segments=3)
```

### 角色部件顺序

1. **头部**
   - 基础形状（球体/立方体）
   - 雕刻面部特征
   - 添加头发

2. **躯干**
   - 胸部/腹部
   - 肩膀
   - 背部

3. **手臂**
   - 上臂
   - 前臂
   - 手部（最后做，最复杂）

4. **腿部**
   - 大腿
   - 小腿
   - 脚部

5. **服装/盔甲**
   - 在身体基础上偏移建模
   - 保持 0.01-0.02 单位间隙避免穿插

---

## 4️⃣ 材质和纹理

### PBR 材质设置

```python
def create_pbr_material(name, base_color, metallic, roughness):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes["Principled BSDF"]
    
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    
    return mat

# 皮肤
skin = create_pbr_material("Skin", (0.95, 0.75, 0.65, 1), 0.0, 0.6)

# 金属盔甲
armor = create_pbr_material("Armor", (0.8, 0.8, 0.8, 1), 0.9, 0.2)

# 布料
cloth = create_pbr_material("Cloth", (0.2, 0.4, 0.7, 1), 0.0, 0.9)
```

### 纹理贴图流程

1. **UV 展开**
   ```python
   bpy.ops.object.mode_set(mode='EDIT')
   bpy.ops.mesh.select_all(action='SELECT')
   bpy.ops.uv.smart_project(angle_limit=66)
   bpy.ops.object.mode_set(mode='OBJECT')
   ```

2. **烘焙纹理**（Substance Painter 或 Blender）

3. **连接纹理节点**
   ```python
   # 基础颜色贴图
   tex_node = nodes.new('ShaderNodeTexImage')
   tex_node.image = bpy.data.images.load('/path/to/albedo.png')
   links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
   
   # 法线贴图
   normal_node = nodes.new('ShaderNodeTexImage')
   normal_node.image = bpy.data.images.load('/path/to/normal.png')
   normal_map_node = nodes.new('ShaderNodeNormalMap')
   links.new(normal_node.outputs['Color'], normal_map_node.inputs['Color'])
   links.new(normal_map_node.outputs['Normal'], bsdf.inputs['Normal'])
   ```

---

## 5️⃣ 灯光和渲染

### 三点布光模板

```python
# 主光（45 度角）
bpy.ops.object.light_add(type='AREA', location=(5, 5, 5))
key = bpy.context.active_object
key.data.energy = 500
key.data.size = 5

# 补光（对面，较弱）
bpy.ops.object.light_add(type='AREA', location=(-3, 3, 3))
fill = bpy.context.active_object
fill.data.energy = 200
fill.data.size = 5

# 轮廓光（背后，突出边缘）
bpy.ops.object.light_add(type='AREA', location=(0, -5, 3))
rim = bpy.context.active_object
rim.data.energy = 300
rim.data.color = (0.8, 0.9, 1.0)
```

### 渲染设置检查清单

- [ ] 渲染引擎：Cycles（高质量）或 Eevee（实时）
- [ ] 采样数：128+（Cycles）
- [ ] 分辨率：1920×1080 或更高
- [ ] 输出格式：PNG（透明背景）或 JPEG
- [ ] 降噪：开启

---

## 6️⃣ 导出模型

### 游戏引擎导出（glTF）

```python
bpy.ops.export_scene.gltf(
    filepath='character.glb',
    export_format='GLB',
    export_apply=True,          # 应用所有修改器
    export_materials='EXPORT',
    export_cameras=False,
    export_lights=False,
    export_yup=True,            # Y 轴向上（Unity/UE）
    export_normals=True,
    export_tangents=True,
    export_uv=True
)
```

### 导出前检查

- [ ] 应用所有变换（Ctrl+A）
- [ ] 应用所有修改器
- [ ] 清理未使用的材质
- [ ] 检查法线方向（Shift+N 重计算）
- [ ] 测试导入目标引擎

---

## ⚠️ 常见问题

### 模型穿插
- 服装/盔甲与身体保持 0.01-0.02 单位间隙
- 使用碰撞检测或手动调整

### 材质丢失
- 导出时勾选 `export_materials`
- 使用 GLB 格式（嵌入材质）
- 检查材质名称无特殊字符

### 比例错误
- 导出前检查单位设置
- 目标引擎中调整缩放因子

### 性能问题
- 减少多边形数量（Decimate 修改器）
- 合并相同材质的物体
- 使用 LOD（多细节层次）

---

## 🎯 优化技巧

### 多边形优化

```python
# 添加精简修改器
bpy.ops.object.modifier_add(type='DECIMATE')
bpy.context.object.modifiers["Decimate"].ratio = 0.5  # 保留 50%
```

### 材质优化

- 合并相同材质的物体（减少绘制调用）
- 使用材质实例（相同参数不同颜色）
- 避免过多透明材质

### UV 优化

- 充分利用 UV 空间（80%+ 利用率）
- 对称部件共用 UV
- 重要区域（脸部）分配更多 UV 空间

---

## 📚 参考资源

- [Blender 角色建模教程](https://www.blender.org/support/tutorials/)
- [glTF 最佳实践](https://github.com/KhronosGroup/glTF-Blender-Exporter)
- [Substance Painter 工作流](https://substance3d.adobe.com/)
