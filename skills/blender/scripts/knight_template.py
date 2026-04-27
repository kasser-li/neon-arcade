# Blender 骑士建模模板脚本
# 可直接运行或作为参考

import bpy
import math

print("=" * 50)
print("🛡️ 骑士建模模板脚本")
print("=" * 50)

# ========== 清理场景 ==========
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# ========== 材质函数 ==========
def create_mat(name, color, metallic=0.5, roughness=0.5, emission=0):
    """创建 PBR 材质"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    
    if emission > 0:
        if 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = emission
        if 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = (emission, emission, emission, 1)
    
    return mat

# ========== 创建材质库 ==========
print("📦 创建材质...")

M_silver = create_mat("Silver", (0.9, 0.9, 0.9, 1), metallic=0.8, roughness=0.25)
M_gold = create_mat("Gold", (1.0, 0.85, 0.1, 1), metallic=0.9, roughness=0.15, emission=0.3)
M_black = create_mat("Black", (0.15, 0.15, 0.15, 1), metallic=0.5, roughness=0.5)
M_blue = create_mat("Blue", (0.2, 0.35, 0.7, 1), roughness=0.8)
M_red = create_mat("Red", (0.6, 0.15, 0.15, 1), roughness=0.8)
M_chainmail = create_mat("Chainmail", (0.5, 0.5, 0.5, 1), metallic=0.7, roughness=0.4)
M_leather = create_mat("Leather", (0.35, 0.25, 0.15, 1), roughness=0.85)
M_glow = create_mat("Glow", (0.0, 0.8, 1.0, 1), emission=1.0)

# ========== 建模函数 ==========
def add_box(name, size, loc, rot=(0,0,0), mat=None):
    """创建立方体"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    if mat: obj.data.materials.append(mat)
    return obj

def add_cylinder(name, radius, depth, loc, rot=(0,0,0), vertices=32, mat=None):
    """创建圆柱体"""
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=vertices, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    if mat: obj.data.materials.append(mat)
    return obj

def add_sphere(name, radius, loc, segments=32, mat=None):
    """创建球体"""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=segments, ring_count=segments//2, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    if mat: obj.data.materials.append(mat)
    return obj

def add_cone(name, radius, depth, loc, rot=(0,0,0), mat=None):
    """创建圆锥体"""
    bpy.ops.mesh.primitive_cone_add(radius1=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    if mat: obj.data.materials.append(mat)
    return obj

# ========== 创建骑士 ==========
print("🏗️ 创建骑士模型...")

# --- 腿部 ---
print("  🦵 腿部...")
# 左腿
add_cylinder("L_Thigh", 0.14, 0.5, (-0.2, 0.5, 0), mat=M_black)
add_sphere("L_Knee", 0.13, (-0.2, 0.22, 0), mat=M_silver)
add_cylinder("L_Shin", 0.11, 0.45, (-0.2, -0.05, 0), mat=M_black)
add_box("L_Foot", (0.16, 0.1, 0.25), (-0.2, -0.32, 0.03), mat=M_black)

# 右腿
add_cylinder("R_Thigh", 0.14, 0.5, (0.2, 0.5, 0), mat=M_black)
add_sphere("R_Knee", 0.13, (0.2, 0.22, 0), mat=M_silver)
add_cylinder("R_Shin", 0.11, 0.45, (0.2, -0.05, 0), mat=M_black)
add_box("R_Foot", (0.16, 0.1, 0.25), (0.2, -0.32, 0.03), mat=M_black)

# --- 躯干 ---
print("  👔 躯干...")
add_cylinder("Abdomen", 0.3, 0.35, (0, 1.05, 0), mat=M_silver)
add_cylinder("Chest", 0.32, 0.7, (0, 1.5, 0), mat=M_silver)
add_box("Chest_Stripe", (0.08, 0.65, 0.05), (0, 1.5, 0.3), mat=M_gold)
add_box("Chest_Top", (0.5, 0.04, 0.05), (0, 1.82, 0.3), mat=M_gold)
add_box("Chest_Bottom", (0.52, 0.04, 0.05), (0, 1.18, 0.3), mat=M_gold)

# --- 头部 ---
print("  🪖 头部...")
add_cylinder("Neck", 0.14, 0.25, (0, 2.0, 0), mat=M_chainmail)
helmet = add_sphere("Helmet", 0.27, (0, 2.32, 0), mat=M_silver)
helmet.scale = (1, 1, 0.85)
add_box("Visor", (0.32, 0.22, 0.18), (0, 2.28, 0.23), mat=M_black)
add_box("Eye_Glow", (0.2, 0.05, 0.03), (0, 2.32, 0.32), mat=M_glow)
add_cone("Helmet_Spike", 0.08, 0.35, (0, 2.65, -0.05), mat=M_gold)
add_cone("Plume", 0.1, 0.5, (0, 2.95, -0.15), rot=(0.35,0,0), mat=M_blue)

# --- 武器 ---
print("  ⚔️ 武器...")
# 剑
add_cylinder("Sword_Hilt", 0.04, 0.28, (0.75, 1.1, 0.35), rot=(0.1,0,-0.15), mat=M_leather)
add_box("Sword_Guard", (0.2, 0.07, 0.07), (0.75, 1.27, 0.35), rot=(0.1,0,-0.15), mat=M_gold)
add_box("Sword_Blade", (0.05, 1.3, 0.012), (0.75, 1.9, 0.35), rot=(0.1,0,-0.15), mat=M_silver)

# 盾牌
add_cylinder("Shield_Body", 0.5, 0.06, (-0.75, 1.1, 0.4), rot=(math.pi/2,0,math.pi/2+0.35), mat=M_silver)
add_torus("Shield_Rim", 0.47, 0.04, (-0.75, 1.1, 0.43), rot=(math.pi/2,0,math.pi/2+0.35), mat=M_gold)

# --- 披风 ---
print("  🧥 披风...")
add_box("Cape_Outer", (0.9, 1.8, 0.03), (0, 1.3, -0.42), rot=(0.2,0,0), mat=M_blue)
add_box("Cape_Inner", (0.85, 1.75, 0.025), (0, 1.3, -0.4), rot=(0.2,0,0), mat=M_red)

# --- 地面 ---
print("  🌍 地面...")
add_cylinder("Ground", 6, 0.1, (0, -0.01, 0), mat=M_black)

# ========== 灯光 ==========
print("💡 创建灯光...")
bpy.ops.object.light_add(type='SUN', location=(5, 8, 5))
bpy.context.active_object.data.energy = 5

bpy.ops.object.light_add(type='AREA', location=(-5, 3, -5))
bpy.context.active_object.data.energy = 3
bpy.context.active_object.data.color = (0.3, 0.5, 1.0)

# ========== 相机 ==========
print("📷 创建相机...")
bpy.ops.object.camera_add(location=(5, 3.5, 5))
camera = bpy.context.active_object
camera.data.lens = 50
bpy.context.scene.camera = camera

# ========== 渲染设置 ==========
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

print("=" * 50)
print("✅ 完成！")
print("=" * 50)
print("\n📖 操作说明：")
print("  • 按 A 全选")
print("  • 按 Z 选 Material Preview")
print("  • 鼠标中键拖拽旋转")
print("  • 按 F12 渲染")
print("  • 文件 > 导出 > glTF 2.0")
print("=" * 50)
