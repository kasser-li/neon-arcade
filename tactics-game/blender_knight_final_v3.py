# Blender 骑士建模 - 三视图精确版
# 严格按照用户提供的三视图比例和细节
# 使用方法：Blender → Scripting → Open → 运行此脚本

import bpy
import math

print("=" * 60)
print("🛡️  骑士建模 - 三视图精确版")
print("=" * 60)

# ========== 清理场景 ==========
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ========== 材质系统 ==========
def create_mat(name, color, metallic=0.5, roughness=0.5, emission=0):
    """创建 PBR 材质 - 兼容 Blender 3.x 和 4.x"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # 创建 Principled BSDF 节点
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # 创建输出节点
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    
    # 连接节点
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # 设置属性
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    
    # 发光（兼容不同版本）
    if emission > 0:
        if 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = emission
        if 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = (emission, emission, emission, 1)
    
    return mat

# ========== 创建材质库（按三视图配色）==========
print("📦 创建材质库...")

# 银色盔甲（主体）
M_silver = create_mat("Silver_Armor", (0.92, 0.92, 0.92, 1), metallic=0.85, roughness=0.2)

# 金色镶边
M_gold = create_mat("Gold_Trim", (1.0, 0.88, 0.15, 1), metallic=0.92, roughness=0.15, emission=0.25)

# 黑色盔甲（腿部/手臂）
M_black = create_mat("Black_Armor", (0.12, 0.12, 0.12, 1), metallic=0.6, roughness=0.45)

# 蓝色披风（外层）
M_blue_cape = create_mat("Blue_Cape", (0.18, 0.32, 0.68, 1), roughness=0.85)

# 红色披风（内衬）
M_red_cape = create_mat("Red_Cape_Lining", (0.65, 0.12, 0.15, 1), roughness=0.85)

# 蓝色战裙
M_blue_skirt = create_mat("Blue_Skirt", (0.22, 0.42, 0.78, 1), roughness=0.75)

# 锁子甲（灰色）
M_chainmail = create_mat("Chainmail", (0.55, 0.55, 0.55, 1), metallic=0.75, roughness=0.4)

# 棕色皮革（剑柄）
M_leather = create_mat("Brown_Leather", (0.38, 0.26, 0.16, 1), roughness=0.88)

# 黑色面罩
M_visor = create_mat("Black_Visor", (0.08, 0.08, 0.08, 1), metallic=0.55, roughness=0.35)

# 发光蓝眼
M_glow_blue = create_mat("Glowing_Eyes", (0.0, 0.75, 1.0, 1), emission=1.0)

# 蓝宝石
M_gem = create_mat("Blue_Gem", (0.15, 0.32, 0.82, 1), metallic=0.85, roughness=0.12)

# ========== 建模辅助函数 ==========
def add_box(name, size, loc, rot=(0,0,0), mat=None):
    """创建立方体"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    if mat:
        obj.data.materials.append(mat)
    return obj

def add_cylinder(name, radius, depth, loc, rot=(0,0,0), vertices=32, mat=None):
    """创建圆柱体"""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, 
        depth=depth, 
        vertices=vertices,
        location=loc, 
        rotation=rot
    )
    obj = bpy.context.active_object
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    return obj

def add_sphere(name, radius, loc, segments=32, mat=None):
    """创建球体"""
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius, 
        segments=segments, 
        ring_count=segments//2,
        location=loc
    )
    obj = bpy.context.active_object
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    return obj

def add_cone(name, radius, depth, loc, rot=(0,0,0), mat=None):
    """创建圆锥体"""
    bpy.ops.mesh.primitive_cone_add(
        radius1=radius, 
        depth=depth, 
        location=loc, 
        rotation=rot
    )
    obj = bpy.context.active_object
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    return obj

def add_torus(name, major_radius, minor_radius, loc, rot=(0,0,0), mat=None):
    """创建圆环"""
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius, 
        minor_radius=minor_radius,
        location=loc, 
        rotation=rot
    )
    obj = bpy.context.active_object
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    return obj

# ========== 创建骑士模型 ==========
print("🏗️  创建骑士模型...")

# --- 腿部（黑色盔甲）---
print("  🦵 腿部...")

# 左腿
add_cylinder("L_Thigh", 0.135, 0.48, (-0.19, 0.48, 0), mat=M_black)
add_sphere("L_Knee", 0.125, (-0.19, 0.21, 0), mat=M_silver)
add_cylinder("L_Shin", 0.105, 0.43, (-0.19, -0.06, 0), mat=M_black)
add_box("L_Foot", (0.155, 0.095, 0.24), (-0.19, -0.33, 0.025), mat=M_black)

# 右腿
add_cylinder("R_Thigh", 0.135, 0.48, (0.19, 0.48, 0), mat=M_black)
add_sphere("R_Knee", 0.125, (0.19, 0.21, 0), mat=M_silver)
add_cylinder("R_Shin", 0.105, 0.43, (0.19, -0.06, 0), mat=M_black)
add_box("R_Foot", (0.155, 0.095, 0.24), (0.19, -0.33, 0.025), mat=M_black)

# --- 战裙（蓝色 + 金色边）---
print("  👗 战裙...")
add_box("Skirt_Front", (0.48, 0.52, 0.075), (0, 0.83, 0.145), mat=M_blue_skirt)
add_box("Skirt_Trim", (0.50, 0.038, 0.085), (0, 0.57, 0.145), mat=M_gold)

# --- 躯干（银色盔甲 + 金色装饰）---
print("  👔 躯干...")

# 腹部
add_cylinder("Abdomen", 0.29, 0.33, (0, 1.03, 0), mat=M_silver)

# 胸部
add_cylinder("Chest", 0.31, 0.68, (0, 1.48, 0), mat=M_silver)

# 胸甲金色竖条
add_box("Chest_Stripe", (0.075, 0.62, 0.048), (0, 1.48, 0.29), mat=M_gold)

# 胸甲金色横条（上）
add_box("Chest_Top_Trim", (0.48, 0.038, 0.048), (0, 1.79, 0.29), mat=M_gold)

# 胸甲金色横条（下）
add_box("Chest_Bottom_Trim", (0.50, 0.038, 0.048), (0, 1.17, 0.29), mat=M_gold)

# 腰部金扣（左右）
add_cylinder("Buckle_L", 0.058, 0.038, (-0.175, 0.865, 0.28), rot=(math.pi/2, 0, 0), mat=M_gold)
add_cylinder("Buckle_R", 0.058, 0.038, (0.175, 0.865, 0.28), rot=(math.pi/2, 0, 0), mat=M_gold)

# --- 肩甲（多层银色 + 金色边）---
print("  🛡️  肩甲...")

# 左肩（4 层）
for i in range(4):
    mat = M_gold if i == 0 else M_silver
    layer_w = 0.245 - i * 0.038
    add_box(f"L_Shoulder_L{i}", 
            (layer_w, 0.058, 0.145),
            (-0.34 + i*0.018, 1.73 - i*0.068, 0.048),
            rot=(0, -0.19, 0.145),
            mat=mat)

add_cylinder("L_Shoulder_Clasp", 0.078, 0.048, (-0.275, 1.805, 0), rot=(math.pi/2, 0, 0), mat=M_gold)

# 右肩（4 层）
for i in range(4):
    mat = M_gold if i == 0 else M_silver
    layer_w = 0.245 - i * 0.038
    add_box(f"R_Shoulder_L{i}",
            (layer_w, 0.058, 0.145),
            (0.34 - i*0.018, 1.73 - i*0.068, 0.048),
            rot=(0, 0.19, -0.145),
            mat=mat)

add_cylinder("R_Shoulder_Clasp", 0.078, 0.048, (0.275, 1.805, 0), rot=(math.pi/2, 0, 0), mat=M_gold)

# --- 手臂（锁子甲 + 银色护臂 + 金色护手）---
print("  💪 手臂...")

# 左臂（持盾）
add_cylinder("L_UpperArm", 0.098, 0.34, (-0.51, 1.58, 0), rot=(0, 0, 0.145), mat=M_chainmail)
add_cylinder("L_Forearm", 0.088, 0.385, (-0.565, 1.285, 0.078), rot=(0, 0, -0.19), mat=M_silver)
add_box("L_Gauntlet", (0.125, 0.135, 0.125), (-0.615, 1.04, 0.145), mat=M_gold)

# 右臂（持剑）
add_cylinder("R_UpperArm", 0.098, 0.34, (0.51, 1.58, 0), rot=(0, 0, -0.145), mat=M_chainmail)
add_cylinder("R_Forearm", 0.088, 0.385, (0.565, 1.285, 0.048), rot=(0, 0, 0.19), mat=M_silver)
add_box("R_Gauntlet", (0.125, 0.135, 0.125), (0.615, 1.04, 0.098), mat=M_gold)

# --- 头部（头盔 + 面罩 + 发光眼 + 羽毛）---
print("  🪖  头部...")

# 脖子（锁子甲）
add_cylinder("Neck", 0.135, 0.24, (0, 1.98, 0), mat=M_chainmail)

# 头盔主体（银色球体，压扁）
helmet = add_sphere("Helmet", 0.265, (0, 2.30, 0), mat=M_silver)
helmet.scale = (1.0, 1.0, 0.83)

# 面罩（黑色）
add_box("Visor", (0.31, 0.21, 0.175), (0, 2.265, 0.225), mat=M_visor)

# 发光眼缝（蓝色）
add_box("Eye_Glow", (0.195, 0.048, 0.028), (0, 2.305, 0.315), mat=M_glow_blue)

# 头盔金色尖顶
add_cone("Helmet_Spike", 0.078, 0.34, (0, 2.63, -0.048), rot=(0, math.pi/4, 0), mat=M_gold)

# 蓝色羽毛
add_cone("Plume", 0.098, 0.48, (0, 2.92, -0.145), rot=(0.34, 0, 0), mat=M_blue_cape)

# --- 剑（右手）---
print("  ⚔️  武器...")

# 剑柄（棕色皮革）
add_cylinder("Sword_Hilt", 0.038, 0.27, (0.74, 1.085, 0.345), rot=(0.095, 0, -0.145), mat=M_leather)

# 护手（金色）
add_box("Sword_Guard", (0.195, 0.068, 0.068), (0.74, 1.255, 0.345), rot=(0.095, 0, -0.145), mat=M_gold)

# 剑身（银色）
add_box("Sword_Blade", (0.048, 1.25, 0.012), (0.74, 1.88, 0.345), rot=(0.095, 0, -0.145), mat=M_silver)

# --- 盾牌（左手）---
print("  🛡️  盾牌...")

shield_x = -0.74
shield_y = 1.085
shield_z = 0.395
shield_rot = (math.pi/2, 0, math.pi/2 + 0.34)

# 盾体（六边形银色）
add_cylinder("Shield_Body", 0.485, 0.058, (shield_x, shield_y, shield_z), rot=shield_rot, vertices=6, mat=M_silver)

# 金色边框
add_torus("Shield_Rim", 0.465, 0.038, (shield_x, shield_y, shield_z + 0.028), rot=shield_rot, mat=M_gold)

# 蓝色徽章（上）
add_cylinder("Shield_Emblem_Top", 0.118, 0.018, (shield_x, shield_y + 0.245, shield_z + 0.038), rot=shield_rot, vertices=8, mat=M_blue_skirt)

# 中央大徽章
add_cylinder("Shield_Emblem_Center", 0.195, 0.018, (shield_x, shield_y, shield_z + 0.038), rot=shield_rot, vertices=8, mat=M_blue_skirt)

# 中央蓝宝石
add_cone("Shield_Gem", 0.098, 0.145, (shield_x, shield_y, shield_z + 0.145), rot=shield_rot, mat=M_gem)

# 金色圆环
add_torus("Shield_Ring", 0.148, 0.018, (shield_x, shield_y, shield_z + 0.048), rot=shield_rot, mat=M_gold)

# --- 披风（蓝色外 + 红色内）---
print("  🧥  披风...")

add_box("Cape_Outer", (0.88, 1.75, 0.028), (0, 1.285, -0.415), rot=(0.19, 0, 0), mat=M_blue_cape)
add_box("Cape_Inner", (0.835, 1.705, 0.024), (0, 1.285, -0.395), rot=(0.19, 0, 0), mat=M_red_cape)

# 金色肩扣
add_sphere("Cape_Clasp_L", 0.088, (-0.375, 1.835, -0.245), mat=M_gold)
add_sphere("Cape_Clasp_R", 0.088, (0.375, 1.835, -0.245), mat=M_gold)

# --- 地面 ---
print("  🌍 地面...")
add_cylinder("Ground", 5.8, 0.095, (0, -0.012, 0), mat=M_black)

# ========== 灯光设置 ==========
print("💡 创建灯光...")

# 主光（太阳光）
bpy.ops.object.light_add(type='SUN', location=(5.0, 7.8, 4.85))
sun = bpy.context.active_object
sun.name = "Main_Light"
sun.data.energy = 5.5
sun.data.color = (1.0, 0.97, 0.92)

# 轮廓光（蓝色，突出边缘）
bpy.ops.object.light_add(type='AREA', location=(-4.85, 2.9, -4.85))
rim = bpy.context.active_object
rim.name = "Rim_Light"
rim.data.energy = 3.2
rim.data.color = (0.28, 0.48, 0.95)
rim.data.size = 4.8

# 补光（暖色，填充阴影）
bpy.ops.object.light_add(type='AREA', location=(0, -1.9, 2.9))
fill = bpy.context.active_object
fill.name = "Fill_Light"
fill.data.energy = 2.2
fill.data.color = (1.0, 0.82, 0.62)
fill.data.size = 2.9

# ========== 相机设置 ==========
print("📷 创建相机...")

bpy.ops.object.camera_add(location=(4.85, 3.4, 4.85))
camera = bpy.context.active_object
camera.name = "Camera"
camera.data.lens = 48
camera.data.clip_end = 100

# 设置相机看向骑士中心
constraint = camera.constraints.new('TRACK_TO')
constraint.target = None
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'

# 设置为活动相机
bpy.context.scene.camera = camera

# ========== 渲染设置 ==========
print("⚙️  配置渲染...")

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
bpy.context.scene.render.image_settings.color_mode = 'RGBA'

# ========== 完成 ==========
print("=" * 60)
print("✅ 骑士模型创建完成！")
print("=" * 60)
print("\n📖 操作说明：")
print("  1. 按 A 全选所有部件")
print("  2. 按 Z 选择 Material Preview 查看材质")
print("  3. 鼠标中键拖拽旋转视角")
print("  4. 滚轮缩放")
print("  5. 按 F12 渲染查看效果")
print("  6. 按 0 切换到相机视图")
print("\n💾 导出模型：")
print("  文件 > 导出 > glTF 2.0 (.glb/.gltf)")
print("  勾选：Export Materials, Apply Modifiers")
print("=" * 60)
print("\n🎨 材质列表：")
print(f"  • 银色盔甲：{M_silver.name}")
print(f"  • 金色镶边：{M_gold.name}")
print(f"  • 黑色盔甲：{M_black.name}")
print(f"  • 蓝色披风：{M_blue_cape.name}")
print(f"  • 红色内衬：{M_red_cape.name}")
print(f"  • 蓝色战裙：{M_blue_skirt.name}")
print(f"  • 锁子甲：{M_chainmail.name}")
print(f"  • 棕色皮革：{M_leather.name}")
print(f"  • 黑色面罩：{M_visor.name}")
print(f"  • 发光蓝眼：{M_glow_blue.name}")
print(f"  • 蓝宝石：{M_gem.name}")
print("=" * 60)
