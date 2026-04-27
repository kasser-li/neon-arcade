# Blender Python API 速查表

## 物体操作

```python
# 选择所有物体
bpy.ops.object.select_all(action='SELECT')

# 取消选择
bpy.ops.object.select_all(action='DESELECT')

# 删除选中物体
bpy.ops.object.delete()

# 获取活动物体
obj = bpy.context.active_object

# 重命名
obj.name = "NewName"

# 设置位置
obj.location = (x, y, z)

# 设置旋转（弧度）
obj.rotation_euler = (rx, ry, rz)

# 设置缩放
obj.scale = (sx, sy, sz)

# 应用变换（相当于 Ctrl+A）
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
```

---

## 几何体创建

### 立方体
```python
bpy.ops.mesh.primitive_cube_add(
    size=1,              # 尺寸
    location=(0, 0, 0),  # 位置
    rotation=(0, 0, 0)   # 旋转（弧度）
)
```

### 圆柱体
```python
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.5,          # 半径
    depth=1.0,           # 高度
    vertices=32,         # 分段数
    location=(0, 0, 0),
    rotation=(0, 0, 0)
)
```

### 球体
```python
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.5,
    segments=32,         # 横向分段
    ring_count=16,       # 纵向分段
    location=(0, 0, 0)
)
```

### 圆锥体
```python
bpy.ops.mesh.primitive_cone_add(
    radius1=0.5,         # 底部半径
    radius2=0.0,         # 顶部半径（0=尖顶）
    depth=1.0,
    vertices=32,
    location=(0, 0, 0)
)
```

### 圆环
```python
bpy.ops.mesh.primitive_torus_add(
    major_radius=1.0,    # 主半径
    minor_radius=0.2,    # 管半径
    ab_major_segments=32,
    ab_minor_segments=8,
    location=(0, 0, 0)
)
```

### 平面
```python
bpy.ops.mesh.primitive_plane_add(
    size=2.0,
    location=(0, 0, 0)
)
```

---

## 材质操作

### 创建材质
```python
mat = bpy.data.materials.new(name="MaterialName")
mat.use_nodes = True
```

### 获取 BSDF 节点
```python
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
if bsdf is None:
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
```

### 设置颜色
```python
# RGBA (0-1)
bsdf.inputs['Base Color'].default_value = (1.0, 0.0, 0.0, 1.0)  # 红色
```

### 设置金属度
```python
bsdf.inputs['Metallic'].default_value = 0.9  # 0-1
```

### 设置粗糙度
```python
bsdf.inputs['Roughness'].default_value = 0.2  # 0-1
```

### 设置发光
```python
# Blender 4.x
bsdf.inputs['Emission Strength'].default_value = 1.0

# Blender 3.x
bsdf.inputs['Emission'].default_value = (1.0, 1.0, 1.0, 1.0)
```

### 应用材质
```python
obj.data.materials.append(mat)
```

---

## 灯光操作

### 创建光源
```python
# 太阳灯（平行光）
bpy.ops.object.light_add(type='SUN', location=(5, 8, 5))

# 点光源
bpy.ops.object.light_add(type='POINT', location=(0, 0, 5))

# 区域光
bpy.ops.object.light_add(type='AREA', location=(-5, 3, -5))

# 聚光灯
bpy.ops.object.light_add(type='SPOT', location=(0, -5, 5))
```

### 设置灯光属性
```python
light = bpy.context.active_object
light.data.energy = 5.0           # 强度
light.data.color = (1.0, 0.9, 0.8)  # 颜色 (RGB)
light.data.size = 5.0             # 区域光尺寸
```

---

## 相机操作

### 创建相机
```python
bpy.ops.object.camera_add(location=(5, 3.5, 5))
camera = bpy.context.active_object
camera.data.lens = 50             # 焦距 (mm)
camera.data.clip_start = 0.1      # 近裁剪面
camera.data.clip_end = 100        # 远裁剪面
```

### 设置活动相机
```python
bpy.context.scene.camera = camera
```

### 添加追踪约束
```python
constraint = camera.constraints.new('TRACK_TO')
constraint.target = target_object
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'
```

---

## 渲染设置

### 渲染引擎
```python
bpy.context.scene.render.engine = 'CYCLES'  # 或 'BLENDER_EEVEE'
```

### Cycles 设置
```python
bpy.context.scene.cycles.samples = 128          # 采样数
bpy.context.scene.cycles.use_denoising = True   # 降噪
```

### 分辨率
```python
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100
```

### 输出格式
```python
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.image_settings.color_mode = 'RGBA'
```

### 渲染图像
```python
bpy.ops.render.render(write_still=True)
```

---

## 导出操作

### glTF/GLB
```python
bpy.ops.export_scene.gltf(
    filepath='/path/to/model.glb',
    export_format='GLB',              # 或 'GLTF_SEPARATE'
    export_apply=True,                # 应用修改器
    export_materials='EXPORT',        # 导出材质
    export_cameras=False,
    export_lights=False,
    export_yup=True                   # Y 轴向上
)
```

### FBX
```python
bpy.ops.export_scene.fbx(
    filepath='/path/to/model.fbx',
    use_selection=True,               # 仅导出选中
    apply_scale_options='FBX_SCALE_ALL',
    object_types={'MESH', 'ARMATURE'},
    bake_space_transform=True
)
```

### OBJ
```python
bpy.ops.export_scene.obj(
    filepath='/path/to/model.obj',
    use_selection=True,
    use_normals=True,
    use_uvs=True
)
```

---

## 数学工具

### 角度转换
```python
import math

# 角度转弧度
radians = math.radians(90)  # 1.5708

# 弧度转角度
degrees = math.degrees(math.pi/2)  # 90.0
```

### 常用值
```python
math.pi       # 3.14159...
math.pi / 2   # 90 度
math.pi / 4   # 45 度
math.pi / 6   # 30 度
```

---

## 调试技巧

### 打印信息
```python
print("物体数量:", len(bpy.data.objects))
print("材质数量:", len(bpy.data.materials))
print("当前物体:", bpy.context.active_object.name)
```

### 列出所有物体
```python
for obj in bpy.data.objects:
    print(f"- {obj.name} (类型：{obj.type})")
```

### 检查材质节点
```python
for mat in bpy.data.materials:
    if mat.use_nodes:
        print(f"材质 {mat.name} 的节点:")
        for node in mat.node_tree.nodes:
            print(f"  - {node.name} ({node.type})")
```

---

## 常用单位换算

| Blender 单位 | 实际长度 |
|-------------|---------|
| 1.0         | 1 米     |
| 0.01        | 1 厘米   |
| 0.001       | 1 毫米   |
| 0.3048      | 1 英尺   |

---

## 快速参考

### 旋转值（弧度）
- 0° = 0
- 45° = π/4 ≈ 0.785
- 90° = π/2 ≈ 1.571
- 180° = π ≈ 3.142

### 典型材质值
| 材质 | 金属度 | 粗糙度 |
|------|--------|--------|
| 镜子 | 1.0    | 0.0    |
| 金属 | 0.8-1.0| 0.2-0.4|
| 塑料 | 0.0    | 0.4-0.6|
| 木材 | 0.0    | 0.6-0.8|
| 布料 | 0.0    | 0.8-1.0|
