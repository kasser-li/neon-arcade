# Blender 骑士建模脚本 - 兼容修复版
# 支持 Blender 3.x 和 4.x

import bpy
import math

# 清除场景默认物体
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ========== 材质 ==========
def get_bsdf_node(mat):
    """获取或创建 Principled BSDF 节点"""
    nodes = mat.node_tree.nodes
    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            return node
    # 找不到就创建
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    return bsdf

def create_material(name, color, metallic=0.5, roughness=0.5, emission=0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = get_bsdf_node(mat)
    
    # 设置颜色
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    
    # 设置发光（兼容不同版本）
    if emission > 0:
        if 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = emission
        elif 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = (emission, emission, emission, 1)
    
    return mat, bsdf

# 创建所有材质
M_silver, _ = create_material("Silver", (0.9, 0.9, 0.9, 1), metallic=0.9, roughness=0.2)
M_gold, M_gold_bsdf = create_material("Gold", (1.0, 0.84, 0, 1), metallic=0.95, roughness=0.15, emission=0.3)
M_black, _ = create_material("Black", (0.1, 0.1, 0.1, 1), metallic=0.7, roughness=0.4)
M_blue, _ = create_material("Blue", (0.12, 0.29, 0.62, 1), roughness=0.9)
M_red, _ = create_material("Red", (0.55, 0.12, 0.12, 1), roughness=0.9)
M_chainmail, _ = create_material("Chainmail", (0.4, 0.4, 0.4, 1), metallic=0.8, roughness=0.5)
M_leather, _ = create_material("Leather", (0.29, 0.22, 0.16, 1), roughness=0.9)
M_glow, _ = create_material("Glow", (0, 0.67, 1, 1), emission=1.0)
M_gem, _ = create_material("Gem", (0.12, 0.25, 0.69, 1), metallic=0.9, roughness=0.1)

# ========== 建模函数 ==========
def create_box(name, size, location, rotation=(0,0,0), material=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    if material:
        obj.data.materials.append(material)
    return obj

def create_cylinder(name, radius, height, location, rotation=(0,0,0), vertices=32, material=None):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=height, vertices=vertices,
        location=location, rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj

def create_sphere(name, radius, location, segments=32, material=None):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius, segments=segments, ring_count=segments//2,
        location=location
    )
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj

def create_cone(name, radius, height, location, rotation=(0,0,0), material=None):
    bpy.ops.mesh.primitive_cone_add(
        radius1=radius, depth=height, location=location, rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj

def create_torus(name, major_radius, minor_radius, location, rotation=(0,0,0), material=None):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius, minor_radius=minor_radius,
        location=location, rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj

# 创建空物体作为父级
knight = bpy.data.objects.new("Knight", None)
bpy.context.collection.objects.link(knight)

# ========== 腿部 ==========
def create_leg(x, name_prefix):
    leg = bpy.data.objects.new(name_prefix, None)
    bpy.context.collection.objects.link(leg)
    leg.parent = knight
    
    thigh = create_cylinder(f"{name_prefix}_Thigh", 0.14, 0.5, (x, 0.5, 0), material=M_black)
    thigh.parent = leg
    
    knee = create_sphere(f"{name_prefix}_Knee", 0.13, (x, 0.22, 0), material=M_silver)
    knee.parent = leg
    
    shin = create_cylinder(f"{name_prefix}_Shin", 0.11, 0.45, (x, -0.05, 0), material=M_black)
    shin.parent = leg
    
    foot = create_box(f"{name_prefix}_Foot", (0.16, 0.1, 0.25), (x, -0.32, 0.03), material=M_black)
    foot.parent = leg

create_leg(-0.2, "LeftLeg")
create_leg(0.2, "RightLeg")

# ========== 战裙 ==========
skirt = create_box("Skirt", (0.5, 0.55, 0.08), (0, 0.85, 0.15), material=M_blue)
skirt.parent = knight

skirt_trim = create_box("Skirt_Trim", (0.52, 0.04, 0.09), (0, 0.58, 0.15), material=M_gold)
skirt_trim.parent = knight

# ========== 躯干 ==========
torso = bpy.data.objects.new("Torso", None)
bpy.context.collection.objects.link(torso)
torso.parent = knight

abdomen = create_cylinder("Abdomen", 0.3, 0.35, (0, 1.05, 0), material=M_silver)
abdomen.parent = torso

chest = create_cylinder("Chest", 0.32, 0.7, (0, 1.5, 0), material=M_silver)
chest.parent = torso

chest_stripe = create_box("Chest_Stripe", (0.08, 0.65, 0.05), (0, 1.5, 0.3), material=M_gold)
chest_stripe.parent = torso

chest_top = create_box("Chest_Top_Trim", (0.5, 0.04, 0.05), (0, 1.82, 0.3), material=M_gold)
chest_top.parent = torso

chest_bottom = create_box("Chest_Bottom_Trim", (0.52, 0.04, 0.05), (0, 1.18, 0.3), material=M_gold)
chest_bottom.parent = torso

for i, x in enumerate([-0.18, 0.18]):
    buckle = create_cylinder(f"Buckle_{i}", 0.06, 0.04, (x, 0.88, 0.28), rotation=(math.pi/2, 0, 0), material=M_gold)
    buckle.parent = torso

# ========== 肩甲 ==========
def create_shoulders(x, name_prefix):
    shoulder = bpy.data.objects.new(name_prefix, None)
    bpy.context.collection.objects.link(shoulder)
    shoulder.parent = knight
    
    for i in range(4):
        mat = M_gold if i == 0 else M_silver
        layer = create_box(
            f"{name_prefix}_Layer{i}",
            (0.25 - i*0.04, 0.06, 0.15),
            (x - i*0.02*math.copysign(1,x), 1.75 - i*0.07, 0.05),
            material=mat
        )
        layer.rotation_euler = (0, math.copysign(0.2, x), -math.copysign(0.15, x))
        layer.parent = shoulder
    
    clasp = create_cylinder(f"{name_prefix}_Clasp", 0.08, 0.05, (x*0.8, 1.82, 0), rotation=(math.pi/2, 0, 0), material=M_gold)
    clasp.parent = shoulder

create_shoulders(-0.35, "LeftShoulder")
create_shoulders(0.35, "RightShoulder")

# ========== 手臂 ==========
def create_arm(x, is_shield, name_prefix):
    arm = bpy.data.objects.new(name_prefix, None)
    bpy.context.collection.objects.link(arm)
    arm.parent = knight
    
    upper = create_cylinder(f"{name_prefix}_Upper", 0.1, 0.35, (x, 1.6, 0), material=M_chainmail)
    upper.rotation_euler = (0, 0, -math.copysign(0.15, x))
    upper.parent = arm
    
    forearm = create_cylinder(f"{name_prefix}_Forearm", 0.09, 0.4, (x*1.1, 1.3, 0.08 if is_shield else 0.05), material=M_silver)
    forearm.rotation_euler = (0, 0, math.copysign(0.2, x))
    forearm.parent = arm
    
    gauntlet = create_box(f"{name_prefix}_Gauntlet", (0.13, 0.14, 0.13), (x*1.15, 1.05, 0.15 if is_shield else 0.1), material=M_gold)
    gauntlet.parent = arm

create_arm(-0.52, True, "LeftArm")
create_arm(0.52, False, "RightArm")

# ========== 头部 ==========
head = bpy.data.objects.new("Head", None)
bpy.context.collection.objects.link(head)
head.parent = knight

neck = create_cylinder("Neck", 0.14, 0.25, (0, 2.0, 0), material=M_chainmail)
neck.parent = head

helmet = create_sphere("Helmet", 0.27, (0, 2.32, 0), material=M_silver)
helmet.scale = (1, 1, 0.8)
helmet.parent = head

visor = create_box("Visor", (0.32, 0.22, 0.18), (0, 2.28, 0.23), material=M_black)
visor.parent = head

eye_glow = create_box("Eye_Glow", (0.2, 0.05, 0.03), (0, 2.32, 0.32), material=M_glow)
eye_glow.parent = head

spike = create_cone("Helmet_Spike", 0.08, 0.35, (0, 2.65, -0.05), material=M_gold)
spike.rotation_euler = (0, math.pi/4, 0)
spike.parent = head

plume = create_cone("Plume", 0.1, 0.5, (0, 2.95, -0.15), rotation=(0.35, 0, 0), material=M_blue)
plume.parent = head

# ========== 剑 ==========
sword = bpy.data.objects.new("Sword", None)
bpy.context.collection.objects.link(sword)
sword.parent = knight

hilt = create_cylinder("Sword_Hilt", 0.04, 0.28, (0, 0, 0), material=M_leather)
hilt.parent = sword

guard = create_box("Sword_Guard", (0.2, 0.07, 0.07), (0, 0.17, 0), material=M_gold)
guard.parent = sword

blade = create_box("Sword_Blade", (0.05, 1.3, 0.012), (0, 0.8, 0), material=M_silver)
blade.parent = sword

sword.location = (0.75, 1.1, 0.35)
sword.rotation_euler = (0.1, 0, -0.15)

# ========== 盾牌 ==========
shield = bpy.data.objects.new("Shield", None)
bpy.context.collection.objects.link(shield)
shield.parent = knight

shield_body = create_cylinder("Shield_Body", 0.5, 0.06, (0, 0, 0), vertices=6, material=M_silver)
shield_body.rotation_euler = (math.pi/2, 0, math.pi/2)
shield_body.parent = shield

shield_rim = create_torus("Shield_Rim", 0.47, 0.04, (0, 0, 0.03), material=M_gold)
shield_rim.rotation_euler = (math.pi/2, 0, math.pi/2)
shield_rim.parent = shield

emblem = create_cylinder("Shield_Emblem", 0.2, 0.02, (0, 0, 0.04), vertices=8, material=M_blue)
emblem.rotation_euler = (math.pi/2, 0, math.pi/2)
emblem.parent = shield

center_gem = create_cone("Shield_Gem", 0.1, 0.15, (0, 0, 0.15), material=M_gem)
center_gem.parent = shield

emblem_ring = create_torus("Shield_Ring", 0.15, 0.02, (0, 0, 0.05), material=M_gold)
emblem_ring.rotation_euler = (math.pi/2, 0, math.pi/2)
emblem_ring.parent = shield

shield.location = (-0.75, 1.1, 0.4)
shield.rotation_euler = (0, 0.35, 0)

# ========== 披风 ==========
cape = bpy.data.objects.new("Cape", None)
bpy.context.collection.objects.link(cape)
cape.parent = knight

cape_outer = create_box("Cape_Outer", (0.9, 1.8, 0.03), (0, 1.3, -0.42), material=M_blue)
cape_outer.rotation_euler = (0.2, 0, 0)
cape_outer.parent = cape

cape_inner = create_box("Cape_Inner", (0.85, 1.75, 0.025), (0, 1.3, -0.4), material=M_red)
cape_inner.rotation_euler = (0.2, 0, 0)
cape_inner.parent = cape

clasp_l = create_sphere("Cape_Clasp_L", 0.09, (-0.38, 1.85, -0.25), material=M_gold)
clasp_l.parent = cape

clasp_r = create_sphere("Cape_Clasp_R", 0.09, (0.38, 1.85, -0.25), material=M_gold)
clasp_r.parent = cape

# ========== 地面 ==========
ground = create_cylinder("Ground", 6, 0.1, (0, -0.01, 0), material=M_black)

# ========== 灯光 ==========
bpy.ops.object.light_add(type='SUN', location=(5, 8, 5))
sun = bpy.context.active_object
sun.name = "Main_Light"
sun.data.energy = 5

bpy.ops.object.light_add(type='AREA', location=(-5, 3, -5))
rim = bpy.context.active_object
rim.name = "Rim_Light"
rim.data.energy = 2
rim.data.color = (0.3, 0.5, 1.0)

# 相机
bpy.ops.object.camera_add(location=(5, 3.5, 5))
camera = bpy.context.active_object
camera.name = "Camera"
camera.data.lens = 50

# 渲染设置
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

print("=" * 50)
print("✅ 骑士模型创建完成！")
print("=" * 50)
print("\n📖 使用说明：")
print("1. 按 F12 渲染查看效果")
print("2. 按 0 切换到相机视图")
print("3. 选中物体可按 Tab 进入编辑模式调整")
print("4. 文件 > 导出 > glTF 2.0 (.glb/.gltf) 导出模型")
print("=" * 50)
