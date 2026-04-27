# Blender 骑士建模脚本 - 最终兼容版
# 支持 Blender 3.x 和 4.x
# 使用方法：打开 Blender → Scripting → Open → 选择此文件 → Run Script

import bpy
import math

print("=" * 50)
print("🛡️ 开始生成骑士模型...")
print("=" * 50)

# ========== 清理场景 ==========
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ========== 材质系统 ==========
def create_material(name, base_color, metallic=0.5, roughness=0.5, emission_strength=0):
    """创建 PBR 材质"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # 清除默认节点
    nodes.clear()
    
    # 创建 Principled BSDF 节点
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # 创建材质输出
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    
    # 连接节点
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # 设置基础颜色
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    
    # 设置发光（兼容不同版本）
    if emission_strength > 0:
        if 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = emission_strength
        if 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = (emission_strength, emission_strength, emission_strength, 1)
    
    return mat

# 创建所有材质
print("📦 创建材质...")

M_silver = create_material("Silver", (0.9, 0.9, 0.9, 1), metallic=0.8, roughness=0.25)
M_gold = create_material("Gold", (1.0, 0.85, 0.1, 1), metallic=0.9, roughness=0.15, emission_strength=0.3)
M_black = create_material("Black", (0.15, 0.15, 0.15, 1), metallic=0.5, roughness=0.5)
M_blue = create_material("Blue", (0.2, 0.35, 0.7, 1), roughness=0.8)
M_red = create_material("Red", (0.6, 0.15, 0.15, 1), roughness=0.8)
M_chainmail = create_material("Chainmail", (0.5, 0.5, 0.5, 1), metallic=0.7, roughness=0.4)
M_leather = create_material("Leather", (0.35, 0.25, 0.15, 1), roughness=0.85)
M_glow = create_material("Glow", (0.0, 0.8, 1.0, 1), emission_strength=1.0)
M_gem = create_material("Gem", (0.15, 0.3, 0.8, 1), metallic=0.8, roughness=0.15)

# ========== 建模辅助函数 ==========
def create_box(name, size, location, rotation=(0,0,0), scale=(1,1,1), material=None):
    """创建立方体"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0] * scale[0], size[1] * scale[1], size[2] * scale[2])
    if material:
        obj.data.materials.append(material)
    return obj

def create_cylinder(name, radius, depth, location, rotation=(0,0,0), vertices=32, material=None):
    """创建圆柱体"""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, 
        depth=depth, 
        vertices=vertices,
        location=location, 
        rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj

def create_sphere(name, radius, location, segments=32, material=None):
    """创建球体"""
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius, 
        segments=segments, 
        ring_count=segments//2,
        location=location
    )
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj

def create_cone(name, radius, depth, location, rotation=(0,0,0), material=None):
    """创建圆锥体"""
    bpy.ops.mesh.primitive_cone_add(
        radius1=radius, 
        depth=depth, 
        location=location, 
        rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj

def create_torus(name, major_radius, minor_radius, location, rotation=(0,0,0), material=None):
    """创建圆环"""
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius, 
        minor_radius=minor_radius,
        location=location, 
        rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj

# 创建骑士父级空物体
print("🏗️ 创建骨架...")
knight = bpy.data.objects.new("Knight", None)
bpy.context.collection.objects.link(knight)

# ========== 腿部 ==========
print("🦵 创建腿部...")

def create_leg(x, side):
    """创建一条腿"""
    leg = bpy.data.objects.new(f"{side}Leg", None)
    bpy.context.collection.objects.link(leg)
    leg.parent = knight
    
    # 大腿（黑色）
    thigh = create_cylinder(f"{side}Thigh", 0.14, 0.5, (x, 0.5, 0), material=M_black)
    thigh.parent = leg
    
    # 膝盖（银色）
    knee = create_sphere(f"{side}Knee", 0.13, (x, 0.22, 0), material=M_silver)
    knee.parent = leg
    
    # 小腿（黑色）
    shin = create_cylinder(f"{side}Shin", 0.11, 0.45, (x, -0.05, 0), material=M_black)
    shin.parent = leg
    
    # 脚（黑色）
    foot = create_box(f"{side}Foot", (0.16, 0.1, 0.25), (x, -0.32, 0.03), material=M_black)
    foot.parent = leg

create_leg(-0.2, "Left")
create_leg(0.2, "Right")

# ========== 战裙 ==========
print("👗 创建战裙...")

skirt = create_box("Skirt", (0.5, 0.55, 0.08), (0, 0.85, 0.15), material=M_blue)
skirt.parent = knight

skirt_trim = create_box("Skirt_Trim", (0.52, 0.04, 0.09), (0, 0.58, 0.15), material=M_gold)
skirt_trim.parent = knight

# ========== 躯干 ==========
print("👔 创建躯干...")

torso = bpy.data.objects.new("Torso", None)
bpy.context.collection.objects.link(torso)
torso.parent = knight

# 腹部
abdomen = create_cylinder("Abdomen", 0.3, 0.35, (0, 1.05, 0), material=M_silver)
abdomen.parent = torso

# 胸部
chest = create_cylinder("Chest", 0.32, 0.7, (0, 1.5, 0), material=M_silver)
chest.parent = torso

# 胸甲金色竖条
chest_stripe = create_box("Chest_Stripe", (0.08, 0.65, 0.05), (0, 1.5, 0.3), material=M_gold)
chest_stripe.parent = torso

# 胸甲金色横条（上）
chest_top = create_box("Chest_Top_Trim", (0.5, 0.04, 0.05), (0, 1.82, 0.3), material=M_gold)
chest_top.parent = torso

# 胸甲金色横条（下）
chest_bottom = create_box("Chest_Bottom_Trim", (0.52, 0.04, 0.05), (0, 1.18, 0.3), material=M_gold)
chest_bottom.parent = torso

# 腰部金扣
for i, x in enumerate([-0.18, 0.18]):
    buckle = create_cylinder(f"Buckle_{i}", 0.06, 0.04, (x, 0.88, 0.28), rotation=(math.pi/2, 0, 0), material=M_gold)
    buckle.parent = torso

# ========== 肩甲 ==========
print("🛡️ 创建肩甲...")

def create_shoulders(x, side):
    """创建肩甲"""
    shoulder = bpy.data.objects.new(f"{side}Shoulder", None)
    bpy.context.collection.objects.link(shoulder)
    shoulder.parent = knight
    
    sign = 1 if x > 0 else -1
    
    for i in range(4):
        mat = M_gold if i == 0 else M_silver
        layer = create_box(
            f"{side}Shoulder_Layer{i}",
            (0.25 - i*0.04, 0.06, 0.15),
            (x - i*0.02*sign, 1.75 - i*0.07, 0.05),
            material=mat
        )
        layer.rotation_euler = (0, sign*0.2, -sign*0.15)
        layer.parent = shoulder
    
    # 肩甲扣
    clasp = create_cylinder(f"{side}Shoulder_Clasp", 0.08, 0.05, (x*0.8, 1.82, 0), rotation=(math.pi/2, 0, 0), material=M_gold)
    clasp.parent = shoulder

create_shoulders(-0.35, "Left")
create_shoulders(0.35, "Right")

# ========== 手臂 ==========
print("💪 创建手臂...")

def create_arm(x, is_shield, side):
    """创建手臂"""
    arm = bpy.data.objects.new(f"{side}Arm", None)
    bpy.context.collection.objects.link(arm)
    arm.parent = knight
    
    sign = 1 if x > 0 else -1
    
    # 锁子甲上臂
    upper = create_cylinder(f"{side}UpperArm", 0.1, 0.35, (x, 1.6, 0), material=M_chainmail)
    upper.rotation_euler = (0, 0, -sign*0.15)
    upper.parent = arm
    
    # 银色护臂
    forearm = create_cylinder(f"{side}Forearm", 0.09, 0.4, (x*1.1, 1.3, 0.08 if is_shield else 0.05), material=M_silver)
    forearm.rotation_euler = (0, 0, sign*0.2)
    forearm.parent = arm
    
    # 金色护手
    gauntlet = create_box(f"{side}Gauntlet", (0.13, 0.14, 0.13), (x*1.15, 1.05, 0.15 if is_shield else 0.1), material=M_gold)
    gauntlet.parent = arm

create_arm(-0.52, True, "Left")
create_arm(0.52, False, "Right")

# ========== 头部 ==========
print("🪖 创建头部...")

head = bpy.data.objects.new("Head", None)
bpy.context.collection.objects.link(head)
head.parent = knight

# 脖子（锁子甲）
neck = create_cylinder("Neck", 0.14, 0.25, (0, 2.0, 0), material=M_chainmail)
neck.parent = head

# 头盔（银色球体）
helmet = create_sphere("Helmet", 0.27, (0, 2.32, 0), material=M_silver)
helmet.scale = (1, 1, 0.85)  # 压扁一点
helmet.parent = head

# 面罩（黑色）
visor = create_box("Visor", (0.32, 0.22, 0.18), (0, 2.28, 0.23), material=M_black)
visor.parent = head

# 发光眼缝（蓝色）
eye_glow = create_box("Eye_Glow", (0.2, 0.05, 0.03), (0, 2.32, 0.32), material=M_glow)
eye_glow.parent = head

# 头盔金色尖顶
spike = create_cone("Helmet_Spike", 0.08, 0.35, (0, 2.65, -0.05), material=M_gold)
spike.rotation_euler = (0, math.pi/4, 0)
spike.parent = head

# 蓝色羽毛
plume = create_cone("Plume", 0.1, 0.5, (0, 2.95, -0.15), rotation=(0.35, 0, 0), material=M_blue)
plume.parent = head

# ========== 剑 ==========
print("⚔️ 创建武器...")

sword = bpy.data.objects.new("Sword", None)
bpy.context.collection.objects.link(sword)
sword.parent = knight

# 剑柄（棕色皮革）
hilt = create_cylinder("Sword_Hilt", 0.04, 0.28, (0, 0, 0), material=M_leather)
hilt.parent = sword

# 护手（金色）
guard = create_box("Sword_Guard", (0.2, 0.07, 0.07), (0, 0.17, 0), material=M_gold)
guard.parent = sword

# 剑身（银色）
blade = create_box("Sword_Blade", (0.05, 1.3, 0.012), (0, 0.8, 0), material=M_silver)
blade.parent = sword

# 设置剑的位置（右手）
sword.location = (0.75, 1.1, 0.35)
sword.rotation_euler = (0.1, 0, -0.15)

# ========== 盾牌 ==========
print("🛡️ 创建盾牌...")

shield = bpy.data.objects.new("Shield", None)
bpy.context.collection.objects.link(shield)
shield.parent = knight

# 盾体（六边形银色）
shield_body = create_cylinder("Shield_Body", 0.5, 0.06, (0, 0, 0), vertices=6, material=M_silver)
shield_body.rotation_euler = (math.pi/2, 0, math.pi/2)
shield_body.parent = shield

# 金色边框
shield_rim = create_torus("Shield_Rim", 0.47, 0.04, (0, 0, 0.03), material=M_gold)
shield_rim.rotation_euler = (math.pi/2, 0, math.pi/2)
shield_rim.parent = shield

# 蓝色徽章
emblem = create_cylinder("Shield_Emblem", 0.2, 0.02, (0, 0, 0.04), vertices=8, material=M_blue)
emblem.rotation_euler = (math.pi/2, 0, math.pi/2)
emblem.parent = shield

# 中央蓝宝石
center_gem = create_cone("Shield_Gem", 0.1, 0.15, (0, 0, 0.15), material=M_gem)
center_gem.parent = shield

# 金色圆环
emblem_ring = create_torus("Shield_Ring", 0.15, 0.02, (0, 0, 0.05), material=M_gold)
emblem_ring.rotation_euler = (math.pi/2, 0, math.pi/2)
emblem_ring.parent = shield

# 设置盾牌位置（左手）
shield.location = (-0.75, 1.1, 0.4)
shield.rotation_euler = (0, 0.35, 0)

# ========== 披风 ==========
print("🧥 创建披风...")

cape = bpy.data.objects.new("Cape", None)
bpy.context.collection.objects.link(cape)
cape.parent = knight

# 蓝色外层
cape_outer = create_box("Cape_Outer", (0.9, 1.8, 0.03), (0, 1.3, -0.42), material=M_blue)
cape_outer.rotation_euler = (0.2, 0, 0)
cape_outer.parent = cape

# 红色内衬
cape_inner = create_box("Cape_Inner", (0.85, 1.75, 0.025), (0, 1.3, -0.4), material=M_red)
cape_inner.rotation_euler = (0.2, 0, 0)
cape_inner.parent = cape

# 金色肩扣（左）
clasp_l = create_sphere("Cape_Clasp_L", 0.09, (-0.38, 1.85, -0.25), material=M_gold)
clasp_l.parent = cape

# 金色肩扣（右）
clasp_r = create_sphere("Cape_Clasp_R", 0.09, (0.38, 1.85, -0.25), material=M_gold)
clasp_r.parent = cape

# ========== 地面 ==========
print("🌍 创建地面...")

ground = create_cylinder("Ground", 6, 0.1, (0, -0.01, 0), material=M_black)

# ========== 灯光 ==========
print("💡 创建灯光...")

# 主光源（太阳）
bpy.ops.object.light_add(type='SUN', location=(5, 8, 5))
sun = bpy.context.active_object
sun.name = "Main_Light"
sun.data.energy = 5
sun.data.color = (1.0, 0.98, 0.9)

# 轮廓光（蓝色）
bpy.ops.object.light_add(type='AREA', location=(-5, 3, -5))
rim = bpy.context.active_object
rim.name = "Rim_Light"
rim.data.energy = 3
rim.data.color = (0.3, 0.5, 1.0)
rim.data.size = 5

# 补光（暖色）
bpy.ops.object.light_add(type='AREA', location=(0, -2, 3))
fill = bpy.context.active_object
fill.name = "Fill_Light"
fill.data.energy = 2
fill.data.color = (1.0, 0.8, 0.6)
fill.data.size = 3

# ========== 相机 ==========
print("📷 创建相机...")

bpy.ops.object.camera_add(location=(5, 3.5, 5))
camera = bpy.context.active_object
camera.name = "Camera"
camera.data.lens = 50
camera.data.clip_end = 100

# 让相机看向骑士
constraint = camera.constraints.new('TRACK_TO')
constraint.target = knight
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'

# ========== 渲染设置 ==========
print("⚙️ 配置渲染设置...")

bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True

# 设置分辨率
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100

# 设置输出格式
bpy.context.scene.render.image_settings.file_format = 'PNG'

# 设置相机为活动相机
bpy.context.scene.camera = camera

print("=" * 50)
print("✅ 骑士模型创建完成！")
print("=" * 50)
print("\n📖 使用说明：")
print("  • 鼠标中键拖拽 - 旋转视角")
print("  • Shift+ 中键 - 平移")
print("  • 滚轮 - 缩放")
print("  • 按 Z 键 - 切换渲染模式（推荐 Material Preview）")
print("  • 按 F12 - 渲染")
print("  • 按 0 - 切换到相机视图")
print("\n💾 导出模型：")
print("  文件 > 导出 > glTF 2.0 (.glb/.gltf)")
print("=" * 50)
