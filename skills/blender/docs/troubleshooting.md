# Blender 建模常见问题排查

## 🔍 问题诊断流程

```
1. 看现象 → 2. 查原因 → 3. 试解决方案 → 4. 验证结果
```

---

## 🎨 材质问题

### Q1: 材质不显示/模型是灰色的

**症状：** 模型显示为灰色，看不到颜色

**原因：**
- 视图模式是 Solid（实体）而不是 Material Preview（材质预览）
- 材质节点未正确连接

**解决方案：**
```python
# 按 Z 键，选择 Material Preview
# 或在视口右上角点击着色方式图标
```

**检查节点连接：**
```python
for mat in bpy.data.materials:
    if mat.use_nodes:
        print(f"材质 {mat.name}:")
        for node in mat.node_tree.nodes:
            print(f"  - {node.name} ({node.type})")
```

---

### Q2: 材质是黑色的

**症状：** 模型或材质显示为纯黑色

**原因：**
- 没有灯光
- 材质发光强度为 0 但期望自发光
- 法线方向错误

**解决方案：**
```python
# 添加灯光
bpy.ops.object.light_add(type='SUN', location=(5, 8, 5))
bpy.context.active_object.data.energy = 5

# 或者切换到 Eevee 引擎（不需要灯光也能看到）
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
```

**检查法线：**
```python
# 进入编辑模式，全选，Shift+N 重计算法线
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
```

---

### Q3: 金属材质看起来像塑料

**症状：** 设置了高金属度，但看起来还是塑料

**原因：**
- 金属度值不够高
- 粗糙度太高
- 没有环境反射

**解决方案：**
```python
# 金属材质标准值
metal = create_material("Metal", (0.8, 0.8, 0.8, 1))
metal.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.95
metal.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.2

# 添加 HDRI 环境贴图增强反射
# World Properties → Color → Environment Texture → 加载 HDRI
```

---

## 💡 灯光问题

### Q4: 场景太暗/什么都看不见

**症状：** 渲染或预览时场景非常暗

**原因：**
- 灯光强度不足
- 灯光方向不对
- 渲染曝光设置问题

**解决方案：**
```python
# 增加灯光强度
bpy.ops.object.light_add(type='SUN', location=(5, 8, 5))
bpy.context.active_object.data.energy = 10  # 默认是 1000W，增加试试

# 添加环境光
bpy.context.scene.world.color = (0.5, 0.5, 0.5)

# 调整曝光（Cycles）
bpy.context.scene.view_settings.exposure = 1.0
```

---

### Q5: 阴影太硬/太黑

**症状：** 阴影边缘锐利或不自然

**原因：**
- 光源尺寸太小
- 阴影采样不足

**解决方案：**
```python
# 增加区域光尺寸（软化阴影）
light = bpy.data.objects['Light']
light.data.type = 'AREA'
light.data.size = 5  # 越大阴影越柔和

# 增加阴影采样
bpy.context.scene.cycles.samples = 256
```

---

## 📐 建模问题

### Q6: 物体位置不对/比例错误

**症状：** 创建的物体不在预期位置

**原因：**
- 坐标系统理解错误
- 父子层级导致坐标偏移
- 缩放未应用

**解决方案：**
```python
# 检查物体位置
obj = bpy.data.objects['ObjectName']
print(f"位置：{obj.location}")
print(f"缩放：{obj.scale}")

# 应用缩放
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.ops.object.transform_apply(scale=True)

# 避免父子层级问题：直接放世界坐标，不设 parent
```

---

### Q7: 模型有黑面/破面

**症状：** 模型表面出现黑色斑块或破洞

**原因：**
- 法线方向不一致
- 面重叠
- 非流形几何

**解决方案：**
```python
# 重计算法线（外部）
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# 移除重叠顶点
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0001)
bpy.ops.object.mode_set(mode='OBJECT')
```

---

## 💾 导出问题

### Q8: 导出后材质丢失

**症状：** 导出的模型在其他软件中没有材质

**原因：**
- 导出设置未勾选材质
- 材质路径问题
- 格式不支持

**解决方案：**
```python
# glTF 导出正确设置
bpy.ops.export_scene.gltf(
    filepath='model.glb',
    export_format='GLB',              # GLB 嵌入所有资源
    export_apply=True,
    export_materials='EXPORT',        # 必须勾选
    export_cameras=False,
    export_lights=False
)

# 或者使用 FBX
bpy.ops.export_scene.fbx(
    filepath='model.fbx',
    use_selection=True,
    path_mode='COPY',                 # 复制纹理
    embed_textures=True               # 嵌入纹理
)
```

---

### Q9: 模型比例在 Unity/UE 中不对

**症状：** 导入游戏引擎后模型太大或太小

**原因：**
- Blender 和游戏引擎单位不一致
- 缩放未应用

**解决方案：**
```python
# Blender 单位设置
bpy.context.scene.unit.system = 'METRIC'
bpy.context.scene.unit.scale_length = 1.0  # 1 Blender 单位 = 1 米

# 导出前应用所有变换
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# glTF 导出设置
bpy.ops.export_scene.gltf(
    filepath='model.glb',
    export_yup=True,                  # Y 轴向上（Unity/UE）
    apply_unit_scale=True
)
```

---

## ⚙️ 性能问题

### Q10: Blender 很卡/渲染慢

**症状：** 操作卡顿，渲染时间过长

**原因：**
- 多边形太多
- 采样数过高
- 修改器未优化

**解决方案：**
```python
# 减少多边形
bpy.ops.object.modifier_add(type='DECIMATE')
bpy.context.object.modifiers["Decimate"].ratio = 0.5

# 降低预览采样
bpy.context.scene.cycles.samples = 64  # 预览用 64，最终渲染用 128+

# 简化视图
bpy.context.scene.display.shading.show_cavity = False
```

---

## 🔧 脚本错误

### Q11: 脚本报错 "KeyError: Principled BSDF"

**原因：** Blender 版本不同，节点名称变化

**解决方案：**
```python
# 兼容写法
def get_bsdf_node(mat):
    nodes = mat.node_tree.nodes
    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    # 找不到就创建
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    return bsdf

# 使用
bsdf = get_bsdf_node(mat)
```

---

### Q12: 脚本运行了但看不到模型

**原因：**
- 相机角度不对
- 模型太小
- 视图没刷新

**解决方案：**
```python
# 视图聚焦所有物体
bpy.ops.view3d.view_all()

# 或者聚焦选中物体
bpy.ops.view3d.view_selected()

# 检查模型是否存在
print(f"场景中有 {len(bpy.data.objects)} 个物体")
for obj in bpy.data.objects:
    print(f"  - {obj.name} 位置：{obj.location}")
```

---

## 📋 检查清单

### 导出前检查

- [ ] 所有变换已应用（Ctrl+A）
- [ ] 所有修改器已应用
- [ ] 法线方向正确（Shift+N）
- [ ] 材质命名无特殊字符
- [ ] UV 已展开
- [ ] 清理未使用的数据块
- [ ] 测试导入目标软件

### 渲染前检查

- [ ] 相机位置和角度
- [ ] 灯光设置
- [ ] 材质正确
- [ ] 渲染分辨率
- [ ] 输出路径和格式
- [ ] 采样数设置

---

## 🆘 快速调试命令

```python
# 列出所有物体
for obj in bpy.data.objects:
    print(f"{obj.name}: 位置={obj.location}, 类型={obj.type}")

# 列出所有材质
for mat in bpy.data.materials:
    print(f"{mat.name}: 节点数={len(mat.node_tree.nodes)}")

# 检查活动物体
print(f"活动物体：{bpy.context.active_object}")

# 重置视图
bpy.ops.view3d.view_all()

# 清理未使用的数据
bpy.ops.outliner.orphans_purge()
```

---

## 📚 更多资源

- [Blender 官方文档](https://docs.blender.org/)
- [Blender Artists 论坛](https://blenderartists.org/)
- [Blender Stack Exchange](https://blender.stackexchange.com/)
