---
name: Blender
description: Create 3D models and characters using Blender's Python API with proper material, lighting, and export workflows.
metadata: {"clawdbot":{"emoji":"🎨","requires":{"bins":["blender"]},"os":["linux","darwin","win32"]}}
---

# Blender Python 建模技能

## 🚀 快速开始

### 运行脚本的标准流程

```python
import bpy
import math

# 1. 清理场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. 创建材质
def create_material(name, color, metallic=0.5, roughness=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    # ... 节点设置
    return mat

# 3. 创建几何体
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
obj = bpy.context.active_object

# 4. 应用材质
obj.data.materials.append(material)

# 5. 设置灯光和相机
# 6. 配置渲染
# 7. 导出模型
```

---

## 📐 核心 API 参考

### 创建基础几何体

```python
# 立方体
bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z), rotation=(rx, ry, rz))

# 圆柱体
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.5, 
    depth=1.0, 
    vertices=32,
    location=(x, y, z)
)

# 球体
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.5,
    segments=32,
    ring_count=16,
    location=(x, y, z)
)

# 圆锥体
bpy.ops.mesh.primitive_cone_add(
    radius1=0.5,
    depth=1.0,
    location=(x, y, z)
)

# 圆环
bpy.ops.mesh.primitive_torus_add(
    major_radius=1.0,
    minor_radius=0.2,
    location=(x, y, z)
)
```

### 获取活动物体

```python
obj = bpy.context.active_object
obj.name = "MyObject"
obj.location = (x, y, z)
obj.rotation_euler = (rx, ry, rz)
obj.scale = (sx, sy, sz)
```

### 材质系统

```python
# 创建材质
mat = bpy.data.materials.new(name="MaterialName")
mat.use_nodes = True

# 获取节点
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# 清除默认节点
nodes.clear()

# 创建 Principled BSDF
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.location = (0, 0)

# 创建输出节点
output = nodes.new('ShaderNodeOutputMaterial')
output.location = (300, 0)

# 连接节点
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# 设置属性
bsdf.inputs['Base Color'].default_value = (R, G, B, A)  # 0-1
bsdf.inputs['Metallic'].default_value = 0.0  # 0-1
bsdf.inputs['Roughness'].default_value = 0.5  # 0-1

# 发光（兼容不同版本）
if 'Emission Strength' in bsdf.inputs:
    bsdf.inputs['Emission Strength'].default_value = 1.0
if 'Emission' in bsdf.inputs:
    bsdf.inputs['Emission'].default_value = (1, 1, 1, 1)

# 应用材质
obj.data.materials.append(mat)
```

---

## 🎨 材质配方

### 金属材质

```python
metal = create_material("Metal", (0.8, 0.8, 0.8, 1))
metal.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.9
metal.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.2
```

### 金色材质

```python
gold = create_material("Gold", (1.0, 0.85, 0.1, 1))
gold.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.95
gold.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.15
gold.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.3
```

### 布料材质

```python
cloth = create_material("Cloth", (0.2, 0.4, 0.8, 1))
cloth.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.0
cloth.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
```

### 发光材质

```python
glow = create_material("Glow", (0.0, 0.8, 1.0, 1))
glow.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.0
```

---

## 💡 灯光设置

### 三点布光法

```python
# 主光（Key Light）
bpy.ops.object.light_add(type='SUN', location=(5, 8, 5))
key_light = bpy.context.active_object
key_light.data.energy = 5
key_light.data.color = (1.0, 0.98, 0.9)

# 轮廓光（Rim Light）
bpy.ops.object.light_add(type='AREA', location=(-5, 3, -5))
rim_light = bpy.context.active_object
rim_light.data.energy = 3
rim_light.data.color = (0.3, 0.5, 1.0)
rim_light.data.size = 5

# 补光（Fill Light）
bpy.ops.object.light_add(type='AREA', location=(0, -2, 3))
fill_light = bpy.context.active_object
fill_light.data.energy = 2
fill_light.data.color = (1.0, 0.8, 0.6)
```

---

## 📷 相机设置

```python
# 创建相机
bpy.ops.object.camera_add(location=(5, 3.5, 5))
camera = bpy.context.active_object
camera.data.lens = 50
camera.data.clip_end = 100

# 设置为活动相机
bpy.context.scene.camera = camera

# 添加追踪约束
constraint = camera.constraints.new('TRACK_TO')
constraint.target = target_object  # 或 None
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'
```

---

## ⚙️ 渲染设置

```python
# 渲染引擎
bpy.context.scene.render.engine = 'CYCLES'

# 采样设置
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True

# 分辨率
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100

# 输出格式
bpy.context.scene.render.image_settings.file_format = 'PNG'
```

---

## 💾 导出模型

### glTF/GLB 导出

```python
bpy.ops.export_scene.gltf(
    filepath='/path/to/model.glb',
    export_format='GLB',
    export_apply=True,
    export_materials='EXPORT',
    export_cameras=False,
    export_lights=False
)
```

### FBX 导出（Unity/UE）

```python
bpy.ops.export_scene.fbx(
    filepath='/path/to/model.fbx',
    use_selection=True,
    apply_scale_options='FBX_SCALE_ALL',
    object_types={'MESH'},
    bake_space_transform=True
)
```

---

## ⚠️ 常见问题

### Q: 材质不显示？
A: 按 Z 键切换到 **Material Preview** 或 **Rendered** 模式。

### Q: 模型太暗/黑屏？
A: 增加灯光强度，或添加环境光：
```python
bpy.ops.object.light_add(type='SUN')
bpy.context.active_object.data.energy = 5
```

### Q: 父子层级问题？
A: Blender 中子物体坐标是相对于父级的。如需世界坐标，不要设置 parent，直接放位置。

### Q: 导出后丢失材质？
A: 导出 glTF 时勾选 `export_materials='EXPORT'`，或使用 GLB 格式（嵌入材质）。

### Q: 模型比例不对？
A: 检查单位设置：
```python
bpy.context.scene.unit.system = 'METRIC'
bpy.context.scene.unit.scale_length = 1.0
```

---

## 📐 角色比例参考

### 写实风格（7.5 头身）

- 头高：约 0.25m
- 总身高：约 1.8m
- 肩宽：约 0.5m（2 个头宽）
- 腿长：约 0.9m（身高 1/2）

### Q 版风格（2-3 头身）

- 头身比：1:2 到 1:3
- 眼睛占脸部 1/3
- 身体缩短，四肢简化

---

## 🎯 最佳实践

1. **命名规范**：所有物体和材质用英文命名（避免导出乱码）
2. **原点归零**：建模完成后，将物体原点移到底部中心
3. **应用变换**：导出前按 Ctrl+A 应用所有变换
4. **材质复用**：相同材质只创建一次，多个物体共享
5. **层级精简**：不必要的父子关系会导出问题，尽量扁平化
6. **测试导出**：复杂场景先导出小样测试

---

## 🔗 参考资源

- [Blender 官方文档](https://docs.blender.org/api/current/)
- [Blender Python API](https://docs.blender.org/api/current/info_quickstart.html)
- [glTF Blender 导出器](https://github.com/KhronosGroup/glTF-Blender-Exporter)
- [Blender Studio](https://studio.blender.org/)
