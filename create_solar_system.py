import bpy
import math
import random

def reset_scene():
    """Clear default objects, materials, curves, collections."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Ensure a main scene exists
    if not bpy.data.scenes:
        bpy.data.scenes.new("Scene")
    scene = bpy.context.scene
    
    # Configure render settings
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 360
    
    return scene

def create_starfield_world():
    """Create a dark cosmic world background with twinkling stars."""
    world = bpy.data.worlds.new("CosmicWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    tree = world.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()
    
    node_out = nodes.new('ShaderNodeOutputWorld')
    node_bg = nodes.new('ShaderNodeBackground')
    node_bg.inputs['Color'].default_value = (0.002, 0.002, 0.006, 1.0)
    node_bg.inputs['Strength'].default_value = 1.0
    
    # Procedural stars using Voronoi texture
    coord = nodes.new('ShaderNodeTexCoord')
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.inputs['Scale'].default_value = 140.0
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.965
    ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp.color_ramp.elements[1].position = 0.985
    ramp.color_ramp.elements[1].color = (1.5, 1.5, 1.8, 1.0) # slightly blue-white star glow
    
    add_node = nodes.new('ShaderNodeMix')
    add_node.data_type = 'RGBA'
    add_node.blend_type = 'ADD'
    add_node.inputs['Factor'].default_value = 1.0
    add_node.inputs[6].default_value = (0.002, 0.002, 0.006, 1.0) # Socket Color A
    
    links.new(coord.outputs['Generated'], voronoi.inputs['Vector'])
    links.new(voronoi.outputs['Distance'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], add_node.inputs[7]) # Socket Color B
    links.new(add_node.outputs[2], node_bg.inputs['Color']) # Output Color
    links.new(node_bg.outputs['Background'], node_out.inputs['Surface'])

def make_material(name, base_color=(0.8, 0.8, 0.8, 1.0), roughness=0.5, metallic=0.0,
                  emission_color=(0.0, 0.0, 0.0, 1.0), emission_strength=0.0, alpha=1.0):
    """Helper to create standard Principled BSDF materials."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = tree.nodes.get('Principled BSDF')
    
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Emission Color'].default_value = emission_color
    bsdf.inputs['Emission Strength'].default_value = emission_strength
    bsdf.inputs['Alpha'].default_value = alpha
    
    if alpha < 0.99:
        mat.blend_method = 'BLEND'
    return mat

def create_sun_material():
    """Create dynamic fiery solar surface material."""
    mat = bpy.data.materials.new(name="M_Sun")
    mat.use_nodes = True
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    coord = nodes.new('ShaderNodeTexCoord')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 5.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.55
    
    ramp = nodes.new('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    cr.elements[0].position = 0.2
    cr.elements[0].color = (1.0, 0.25, 0.02, 1.0) # Deep solar orange/red
    cr.elements[1].position = 0.7
    cr.elements[1].color = (1.0, 0.85, 0.35, 1.0) # Brilliant incandescent gold
    e_extra = cr.elements.new(0.95)
    e_extra.color = (1.0, 1.0, 0.9, 1.0) # White core hotspot
    
    bsdf.inputs['Roughness'].default_value = 0.9
    bsdf.inputs['Emission Strength'].default_value = 14.0
    
    links.new(coord.outputs['Object'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Emission Color'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_earth_material():
    """Create 100% Procedural Earth surface with glossy oceans, continents, polar ice caps, terrain bump and atmospheric rim glow."""
    mat = bpy.data.materials.new(name="M_Earth_Surface")
    mat.use_nodes = True
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    coord = nodes.new('ShaderNodeTexCoord')
    
    # 1. Continents & Terrain Noise
    noise_land = nodes.new('ShaderNodeTexNoise')
    noise_land.inputs['Scale'].default_value = 2.8
    noise_land.inputs['Detail'].default_value = 12.0
    noise_land.inputs['Roughness'].default_value = 0.62
    noise_land.inputs['Distortion'].default_value = 0.25
    
    ramp_land = nodes.new('ShaderNodeValToRGB')
    cr_l = ramp_land.color_ramp
    cr_l.elements[0].position = 0.00
    cr_l.elements[0].color = (0.012, 0.055, 0.26, 1.0) # Deep Ocean
    cr_l.elements[1].position = 1.00
    cr_l.elements[1].color = (0.85, 0.85, 0.88, 1.0) # Snow mountain peak
    
    e1 = cr_l.elements.new(0.48)
    e1.color = (0.025, 0.20, 0.40, 1.0) # Shallow coastal blue
    e2 = cr_l.elements.new(0.505)
    e2.color = (0.58, 0.52, 0.35, 1.0) # Beach sand
    e3 = cr_l.elements.new(0.53)
    e3.color = (0.05, 0.28, 0.08, 1.0) # Lush green land
    e4 = cr_l.elements.new(0.68)
    e4.color = (0.22, 0.30, 0.12, 1.0) # Highlands / Savannah
    e5 = cr_l.elements.new(0.80)
    e5.color = (0.38, 0.28, 0.18, 1.0) # Rocky mountains
    
    # 2. Polar Ice Caps: North & South Poles using abs(Z)
    sep_xyz = nodes.new('ShaderNodeSeparateXYZ')
    math_abs = nodes.new('ShaderNodeMath')
    math_abs.operation = 'ABSOLUTE'
    
    ramp_poles = nodes.new('ShaderNodeValToRGB')
    cr_p = ramp_poles.color_ramp
    cr_p.elements[0].position = 0.72
    cr_p.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    cr_p.elements[1].position = 0.86
    cr_p.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    
    # Mix polar ice with terrain
    mix_ice = nodes.new('ShaderNodeMix')
    mix_ice.data_type = 'RGBA'
    mix_ice.blend_type = 'MIX'
    mix_ice.inputs[7].default_value = (0.95, 0.98, 1.0, 1.0) # Ice Cap White
    
    # 3. Specular / Roughness Map (Glossy water, matte land)
    ramp_rough = nodes.new('ShaderNodeValToRGB')
    cr_r = ramp_rough.color_ramp
    cr_r.elements[0].position = 0.48
    cr_r.elements[0].color = (0.08, 0.08, 0.08, 1.0) # Water = super reflective/shiny
    cr_r.elements[1].position = 0.52
    cr_r.elements[1].color = (0.85, 0.85, 0.85, 1.0) # Land = rough matte
    
    # 4. Mountain Terrain Bump Relief
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.35
    bump.inputs['Distance'].default_value = 0.15
    
    # 5. Atmospheric Blue Fresnel Rim Glow
    lw = nodes.new('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.25
    
    ramp_rim = nodes.new('ShaderNodeValToRGB')
    cr_rim = ramp_rim.color_ramp
    cr_rim.elements[0].position = 0.55
    cr_rim.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    cr_rim.elements[1].position = 0.92
    cr_rim.elements[1].color = (0.15, 0.55, 1.0, 1.0) # Atmospheric blue haze
    
    # Wiring
    links.new(coord.outputs['Object'], noise_land.inputs['Vector'])
    links.new(coord.outputs['Object'], sep_xyz.inputs['Vector'])
    links.new(sep_xyz.outputs['Z'], math_abs.inputs[0])
    links.new(math_abs.outputs['Value'], ramp_poles.inputs['Fac'])
    
    links.new(noise_land.outputs['Fac'], ramp_land.inputs['Fac'])
    links.new(ramp_poles.outputs['Color'], mix_ice.inputs['Factor'])
    links.new(ramp_land.outputs['Color'], mix_ice.inputs[6])
    links.new(mix_ice.outputs[2], bsdf.inputs['Base Color'])
    
    # Roughness & Bump
    links.new(noise_land.outputs['Fac'], ramp_rough.inputs['Fac'])
    links.new(ramp_rough.outputs['Color'], bsdf.inputs['Roughness'])
    links.new(noise_land.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    # Rim Glow
    links.new(lw.outputs['Fresnel'], ramp_rim.inputs['Fac'])
    links.new(ramp_rim.outputs['Color'], bsdf.inputs['Emission Color'])
    bsdf.inputs['Emission Strength'].default_value = 2.0
    
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_earth_cloud_material():
    """Create 100% Procedural 3D Cloud sphere with realistic weather swirls and alpha transparency."""
    mat = bpy.data.materials.new(name="M_Earth_Clouds")
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    coord = nodes.new('ShaderNodeTexCoord')
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 4.2
    noise.inputs['Detail'].default_value = 7.0
    noise.inputs['Roughness'].default_value = 0.65
    noise.inputs['Distortion'].default_value = 0.35
    
    ramp = nodes.new('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    cr.elements[0].position = 0.49
    cr.elements[0].color = (0.0, 0.0, 0.0, 1.0) # Transparent gap
    cr.elements[1].position = 0.68
    cr.elements[1].color = (0.92, 0.92, 0.95, 1.0) # Cloud density
    
    bsdf.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.95
    
    links.new(coord.outputs['Object'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Alpha'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_jupiter_material():
    """Create Jupiter's banded turbulent atmosphere."""
    mat = bpy.data.materials.new(name="M_Jupiter")
    mat.use_nodes = True
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    coord = nodes.new('ShaderNodeTexCoord')
    
    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value = 1.8
    wave.inputs['Distortion'].default_value = 4.5
    wave.inputs['Detail'].default_value = 6.0
    wave.inputs['Detail Scale'].default_value = 1.5
    
    ramp = nodes.new('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    cr.elements[0].position = 0.08
    cr.elements[0].color = (0.78, 0.65, 0.48, 1.0) # Warm beige
    cr.elements[1].position = 0.35
    cr.elements[1].color = (0.55, 0.25, 0.12, 1.0) # Terracotta stripe
    e1 = cr.elements.new(0.60)
    e1.color = (0.85, 0.78, 0.68, 1.0) # Cream zone
    e2 = cr.elements.new(0.82)
    e2.color = (0.68, 0.35, 0.18, 1.0) # Brown band
    
    links.new(coord.outputs['Object'], wave.inputs['Vector'])
    links.new(wave.outputs['Color'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.65
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_mars_material():
    """Create Mars material with rusty red surface, dark terrain and white polar ice caps."""
    mat = bpy.data.materials.new(name="M_Mars")
    mat.use_nodes = True
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    coord = nodes.new('ShaderNodeTexCoord')
    sep_xyz = nodes.new('ShaderNodeSeparateXYZ')
    
    # Polar ice check: abs(Z)
    math_abs = nodes.new('ShaderNodeMath')
    math_abs.operation = 'ABSOLUTE'
    
    ramp_ice = nodes.new('ShaderNodeValToRGB')
    cr_ice = ramp_ice.color_ramp
    cr_ice.elements[0].position = 0.52
    cr_ice.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    cr_ice.elements[1].position = 0.58
    cr_ice.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    
    # Surface terrain noise
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 8.0
    noise.inputs['Detail'].default_value = 5.0
    
    ramp_rust = nodes.new('ShaderNodeValToRGB')
    cr_rust = ramp_rust.color_ramp
    cr_rust.elements[0].position = 0.35
    cr_rust.elements[0].color = (0.42, 0.16, 0.07, 1.0) # Dark basaltic volcanic basin
    cr_rust.elements[1].position = 0.65
    cr_rust.elements[1].color = (0.82, 0.32, 0.13, 1.0) # Rusty iron oxide dust
    
    # Mix ice with rust surface
    mix = nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.blend_type = 'MIX'
    mix.inputs[7].default_value = (0.92, 0.94, 0.98, 1.0) # Ice white
    
    links.new(coord.outputs['Object'], sep_xyz.inputs['Vector'])
    links.new(sep_xyz.outputs['Z'], math_abs.inputs[0])
    links.new(math_abs.outputs['Value'], ramp_ice.inputs['Fac'])
    
    links.new(coord.outputs['Object'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp_rust.inputs['Fac'])
    
    links.new(ramp_ice.outputs['Color'], mix.inputs['Factor'])
    links.new(ramp_rust.outputs['Color'], mix.inputs[6])
    
    links.new(mix.outputs[2], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.8
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_saturn_ring_material():
    """Create Saturn's multi-ring material with Cassini Division and icy dust transparency."""
    mat = bpy.data.materials.new(name="M_SaturnRings")
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    coord = nodes.new('ShaderNodeTexCoord')
    sep_xyz = nodes.new('ShaderNodeSeparateXYZ')
    
    # Calculate radius in XY: sqrt(x^2 + y^2)
    math_x2 = nodes.new('ShaderNodeMath')
    math_x2.operation = 'POWER'
    math_x2.inputs[1].default_value = 2.0
    
    math_y2 = nodes.new('ShaderNodeMath')
    math_y2.operation = 'POWER'
    math_y2.inputs[1].default_value = 2.0
    
    math_add = nodes.new('ShaderNodeMath')
    math_add.operation = 'ADD'
    
    math_dist = nodes.new('ShaderNodeMath')
    math_dist.operation = 'SQRT'
    
    # Map range [2.7, 5.7] to [0.0, 1.0]
    map_range = nodes.new('ShaderNodeMapRange')
    map_range.inputs['From Min'].default_value = 2.7
    map_range.inputs['From Max'].default_value = 5.7
    map_range.inputs['To Min'].default_value = 0.0
    map_range.inputs['To Max'].default_value = 1.0
    
    links.new(coord.outputs['Object'], sep_xyz.inputs['Vector'])
    links.new(sep_xyz.outputs['X'], math_x2.inputs[0])
    links.new(sep_xyz.outputs['Y'], math_y2.inputs[0])
    links.new(math_x2.outputs['Value'], math_add.inputs[0])
    links.new(math_y2.outputs['Value'], math_add.inputs[1])
    links.new(math_add.outputs['Value'], math_dist.inputs[0])
    links.new(math_dist.outputs['Value'], map_range.inputs['Value'])
    
    # Map normalized distance to Color & Alpha
    ramp_color = nodes.new('ShaderNodeValToRGB')
    cr_c = ramp_color.color_ramp
    cr_c.elements[0].position = 0.05
    cr_c.elements[0].color = (0.55, 0.48, 0.38, 1.0) # C Ring inner dusky
    cr_c.elements[1].position = 0.95
    cr_c.elements[1].color = (0.85, 0.78, 0.65, 1.0) # A Ring outer ice
    e_c1 = cr_c.elements.new(0.35)
    e_c1.color = (0.92, 0.85, 0.72, 1.0) # B Ring bright dense ice
    e_c2 = cr_c.elements.new(0.62)
    e_c2.color = (0.22, 0.18, 0.14, 1.0) # Cassini division gap
    
    ramp_alpha = nodes.new('ShaderNodeValToRGB')
    cr_a = ramp_alpha.color_ramp
    cr_a.elements[0].position = 0.02
    cr_a.elements[0].color = (0.0, 0.0, 0.0, 1.0) # transparent inner edge
    cr_a.elements[1].position = 0.98
    cr_a.elements[1].color = (0.0, 0.0, 0.0, 1.0) # transparent outer edge
    ea1 = cr_a.elements.new(0.12)
    ea1.color = (0.40, 0.40, 0.40, 1.0) # C ring faint
    ea2 = cr_a.elements.new(0.35)
    ea2.color = (0.95, 0.95, 0.95, 1.0) # B ring dense opaque
    ea3 = cr_a.elements.new(0.60)
    ea3.color = (0.02, 0.02, 0.02, 1.0) # Cassini Division
    ea4 = cr_a.elements.new(0.75)
    ea4.color = (0.80, 0.80, 0.80, 1.0) # A ring
    
    links.new(map_range.outputs['Result'], ramp_color.inputs['Fac'])
    links.new(map_range.outputs['Result'], ramp_alpha.inputs['Fac'])
    
    links.new(ramp_color.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(ramp_alpha.outputs['Color'], bsdf.inputs['Alpha'])
    bsdf.inputs['Roughness'].default_value = 0.4
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_orbit_ring_curve(radius, name, collection, mat):
    """Create a sleek visual orbit line in 3D space."""
    curve_data = bpy.data.curves.new(name=f"{name}_OrbitPath", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.04
    curve_data.bevel_resolution = 3
    
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(3) # 4 points total
    k = 0.5522847498 * radius # handle vector length for perfect quarter circle
    
    coords = [
        ((radius, 0.0, 0.0), (radius, -k, 0.0), (radius, k, 0.0)),
        ((0.0, radius, 0.0), (k, radius, 0.0), (-k, radius, 0.0)),
        ((-radius, 0.0, 0.0), (-radius, k, 0.0), (-radius, -k, 0.0)),
        ((0.0, -radius, 0.0), (-k, -radius, 0.0), (k, -radius, 0.0)),
    ]
    
    for idx, (co, h_left, h_right) in enumerate(coords):
        p = spline.bezier_points[idx]
        p.co = co
        p.handle_left = h_left
        p.handle_right = h_right
        p.handle_left_type = 'FREE'
        p.handle_right_type = 'FREE'
        
    spline.use_cyclic_u = True
    
    obj = bpy.data.objects.new(f"{name}_OrbitLine", curve_data)
    obj.data.materials.append(mat)
    collection.objects.link(obj)
    return obj

def create_ring_mesh(name, r_in, r_out, segments=96):
    """Create clean planar ring mesh with UV coordinates."""
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    verts = []
    faces = []
    
    for i in range(segments):
        angle = 2.0 * math.pi * i / segments
        ca, sa = math.cos(angle), math.sin(angle)
        verts.append((r_in * ca, r_in * sa, 0.0))
        verts.append((r_out * ca, r_out * sa, 0.0))
        
    for i in range(segments):
        v0 = i * 2
        v1 = v0 + 1
        v2 = ((i + 1) % segments) * 2 + 1
        v3 = ((i + 1) % segments) * 2
        faces.append((v0, v1, v2, v3))
        
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return obj

def build_solar_system():
    scene = reset_scene()
    create_starfield_world()
    
    # Organize collections
    col_sun = bpy.data.collections.new("01_Sun_and_Lighting")
    col_planets = bpy.data.collections.new("02_Planets")
    col_orbits = bpy.data.collections.new("03_Orbit_Paths")
    col_asteroids = bpy.data.collections.new("04_Asteroid_Belt")
    col_setup = bpy.data.collections.new("05_Camera_and_Setup")
    
    scene.collection.children.link(col_sun)
    scene.collection.children.link(col_planets)
    scene.collection.children.link(col_orbits)
    scene.collection.children.link(col_asteroids)
    scene.collection.children.link(col_setup)
    
    # Orbit line material (subtle glowing cyan/blue)
    mat_orbit = make_material(
        "M_OrbitPath",
        base_color=(0.1, 0.45, 0.85, 1.0),
        roughness=0.2,
        emission_color=(0.15, 0.5, 0.95, 1.0),
        emission_strength=2.5
    )
    
    # ------------------ 1. SUN & LIGHTING ------------------
    # Sun Sphere
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=4.2, location=(0, 0, 0))
    sun_obj = bpy.context.active_object
    sun_obj.name = "Sun"
    sun_obj.data.name = "Sun_Mesh"
    col_sun.objects.link(sun_obj)
    scene.collection.objects.unlink(sun_obj)
    sun_obj.data.materials.append(create_sun_material())
    
    # Sun Rotation driver
    d_sun = sun_obj.driver_add('rotation_euler', 2)
    d_sun.driver.expression = "frame * 0.005"
    
    # Sun Light (Point Light at center)
    light_data = bpy.data.lights.new(name="Sun_PointLight", type='POINT')
    light_data.energy = 18000.0
    light_data.shadow_soft_size = 4.0
    light_data.color = (1.0, 0.96, 0.90)
    light_obj = bpy.data.objects.new(name="Sun_Light", object_data=light_data)
    col_sun.objects.link(light_obj)
    
    # Ambient fill light (very subtle)
    amb_data = bpy.data.lights.new(name="Cosmic_AmbientLight", type='POINT')
    amb_data.energy = 500.0
    amb_data.shadow_soft_size = 50.0
    amb_data.color = (0.2, 0.35, 0.6)
    amb_obj = bpy.data.objects.new(name="Cosmic_Ambient", object_data=amb_data)
    amb_obj.location = (0, 0, 15)
    col_sun.objects.link(amb_obj)
    
    # ------------------ 2. PLANETS CONFIG ------------------
    # Materials for various planets
    mat_mercury = make_material("M_Mercury", (0.45, 0.42, 0.39, 1.0), roughness=0.85)
    mat_venus = make_material("M_Venus", (0.86, 0.74, 0.52, 1.0), roughness=0.55)
    mat_earth = create_earth_material()
    mat_earth_clouds = create_earth_cloud_material()
    mat_moon = make_material("M_Moon", (0.6, 0.6, 0.62, 1.0), roughness=0.9)
    mat_mars = create_mars_material()
    mat_jupiter = create_jupiter_material()
    mat_saturn = make_material("M_Saturn", (0.83, 0.74, 0.56, 1.0), roughness=0.5)
    mat_saturn_rings = create_saturn_ring_material()
    mat_uranus = make_material("M_Uranus", (0.40, 0.76, 0.82, 1.0), roughness=0.35)
    mat_uranus_rings = make_material("M_UranusRings", (0.6, 0.85, 0.95, 0.4), roughness=0.3, alpha=0.35)
    mat_neptune = make_material("M_Neptune", (0.08, 0.28, 0.86, 1.0), roughness=0.3)
    mat_pluto = make_material("M_Pluto", (0.58, 0.50, 0.44, 1.0), roughness=0.8)
    mat_rock = make_material("M_Asteroid", (0.35, 0.32, 0.30, 1.0), roughness=0.95)
    
    planets_data = [
        # (Name, Distance, Radius, Mat, OrbitSpeedFactor, AxialTiltRad, SpinSpeed, ExtraConfig)
        ("Mercury", 8.0, 0.55, mat_mercury, 0.040, 0.035, 0.015, {}),
        ("Venus", 12.5, 0.92, mat_venus, 0.026, 3.09, -0.008, {}),
        ("Earth", 18.0, 1.05, mat_earth, 0.018, 0.409, 0.05, {"has_moon": True}),
        ("Mars", 24.0, 0.68, mat_mars, 0.013, 0.439, 0.045, {}),
        ("Jupiter", 39.0, 2.50, mat_jupiter, 0.0075, 0.054, 0.075, {"moons": 4}),
        ("Saturn", 53.0, 2.05, mat_saturn, 0.0050, 0.466, 0.065, {"rings": "saturn"}),
        ("Uranus", 67.0, 1.45, mat_uranus, 0.0033, 1.706, 0.042, {"rings": "uranus"}),
        ("Neptune", 80.0, 1.40, mat_neptune, 0.0022, 0.494, 0.043, {"moons": 1}),
        ("Pluto", 93.0, 0.38, mat_pluto, 0.0016, 2.09, 0.012, {"inclination": 0.297}),
    ]
    
    for p_name, dist, rad, mat, orb_speed, tilt, spin_speed, extra in planets_data:
        # 1. Orbit path curve
        create_orbit_ring_curve(dist, p_name, col_orbits, mat_orbit)
        
        # 2. Orbital Pivot Empty at origin
        pivot = bpy.data.objects.new(f"Pivot_{p_name}", None)
        col_planets.objects.link(pivot)
        
        # Apply orbital inclination if any (e.g. Pluto)
        if "inclination" in extra:
            pivot.rotation_euler.x = extra["inclination"]
            
        # Drive orbital revolution
        d_orb = pivot.driver_add('rotation_euler', 2)
        d_orb.driver.expression = f"frame * {orb_speed}"
        
        # 3. Planet Object
        bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=rad, location=(dist, 0.0, 0.0))
        planet_obj = bpy.context.active_object
        planet_obj.name = p_name
        planet_obj.data.name = f"{p_name}_Mesh"
        col_planets.objects.link(planet_obj)
        scene.collection.objects.unlink(planet_obj)
        
        planet_obj.data.materials.append(mat)
        planet_obj.parent = pivot
        planet_obj.rotation_euler.x = tilt
        
        # Axial rotation driver
        d_spin = planet_obj.driver_add('rotation_euler', 2)
        d_spin.driver.expression = f"frame * {spin_speed}"
        
        # 4. Earth's Dedicated 3D Clouds Sphere & Moon
        if extra.get("has_moon"):
            # 3D Cloud Sphere hovering just above Earth surface
            bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=rad * 1.018, location=(0, 0, 0))
            cloud_obj = bpy.context.active_object
            cloud_obj.name = "Earth_Clouds"
            cloud_obj.data.name = "Earth_Clouds_Mesh"
            col_planets.objects.link(cloud_obj)
            scene.collection.objects.unlink(cloud_obj)
            cloud_obj.data.materials.append(mat_earth_clouds)
            cloud_obj.parent = planet_obj
            
            # Independent atmospheric cloud drift driver
            d_clouds = cloud_obj.driver_add('rotation_euler', 2)
            d_clouds.driver.expression = "frame * 0.056"
            
            # Moon
            bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.28, location=(dist + 2.2, 0, 0))
            moon_obj = bpy.context.active_object
            moon_obj.name = "Moon"
            moon_obj.data.name = "Moon_Mesh"
            col_planets.objects.link(moon_obj)
            scene.collection.objects.unlink(moon_obj)
            moon_obj.data.materials.append(mat_moon)
            
            # Moon Orbit Empty located at Earth
            moon_pivot = bpy.data.objects.new("Pivot_Moon", None)
            moon_pivot.location = (dist, 0, 0)
            moon_pivot.parent = pivot
            col_planets.objects.link(moon_pivot)
            
            moon_obj.parent = moon_pivot
            moon_obj.location = (2.2, 0, 0)
            d_moon = moon_pivot.driver_add('rotation_euler', 2)
            d_moon.driver.expression = "frame * 0.09"
            
        # 5. Saturn Rings
        if extra.get("rings") == "saturn":
            ring_obj = create_ring_mesh("Saturn_Rings", r_in=2.7, r_out=5.7, segments=96)
            ring_obj.data.materials.append(mat_saturn_rings)
            col_planets.objects.link(ring_obj)
            ring_obj.parent = planet_obj
            ring_obj.location = (0, 0, 0)
            
        # 6. Uranus Rings
        if extra.get("rings") == "uranus":
            u_ring = create_ring_mesh("Uranus_Rings", r_in=1.9, r_out=2.6, segments=64)
            u_ring.data.materials.append(mat_uranus_rings)
            col_planets.objects.link(u_ring)
            u_ring.parent = planet_obj
            u_ring.location = (0, 0, 0)
            
        # 7. Jupiter Galilean Moons
        if extra.get("moons") == 4:
            j_moons = [
                ("Io", 3.4, 0.16, (0.85, 0.75, 0.2, 1.0), 0.12),
                ("Europa", 4.3, 0.14, (0.85, 0.9, 0.95, 1.0), 0.08),
                ("Ganymede", 5.4, 0.22, (0.55, 0.52, 0.48, 1.0), 0.05),
                ("Callisto", 6.7, 0.20, (0.35, 0.35, 0.35, 1.0), 0.03),
            ]
            for m_name, m_d, m_r, m_col, m_spd in j_moons:
                m_mat = make_material(f"M_{m_name}", m_col, roughness=0.8)
                m_piv = bpy.data.objects.new(f"Pivot_{m_name}", None)
                m_piv.location = (dist, 0, 0)
                m_piv.parent = pivot
                col_planets.objects.link(m_piv)
                
                bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=m_r, location=(m_d, 0, 0))
                m_obj = bpy.context.active_object
                m_obj.name = m_name
                col_planets.objects.link(m_obj)
                scene.collection.objects.unlink(m_obj)
                m_obj.data.materials.append(m_mat)
                m_obj.parent = m_piv
                
                d_jm = m_piv.driver_add('rotation_euler', 2)
                d_jm.driver.expression = f"frame * {m_spd}"
                
    # ------------------ 3. ASTEROID BELT ------------------
    # Generate 140 rocky asteroids between Mars and Jupiter (~28 to 33.5)
    random.seed(42)
    ast_pivot = bpy.data.objects.new("Pivot_AsteroidBelt", None)
    col_asteroids.objects.link(ast_pivot)
    d_ast = ast_pivot.driver_add('rotation_euler', 2)
    d_ast.driver.expression = "frame * 0.0095"
    
    for i in range(130):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(27.5, 33.5)
        z = random.uniform(-0.8, 0.8)
        scale_val = random.uniform(0.06, 0.18)
        
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=scale_val, location=(r * math.cos(angle), r * math.sin(angle), z))
        ast_obj = bpy.context.active_object
        ast_obj.name = f"Asteroid_{i:03d}"
        col_asteroids.objects.link(ast_obj)
        scene.collection.objects.unlink(ast_obj)
        
        ast_obj.data.materials.append(mat_rock)
        ast_obj.parent = ast_pivot
        ast_obj.rotation_euler = (random.uniform(0, 6.28), random.uniform(0, 6.28), random.uniform(0, 6.28))
        
    # ------------------ 4. CAMERA & CINEMATICS ------------------
    cam_data = bpy.data.cameras.new("Main_Camera")
    cam_data.lens = 35.0
    cam_data.clip_end = 1000.0
    
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    cam_obj.location = (68.0, -96.0, 52.0)
    col_setup.objects.link(cam_obj)
    scene.camera = cam_obj
    
    # Track To Sun
    tt = cam_obj.constraints.new(type='TRACK_TO')
    tt.target = sun_obj
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'
    
    # Set 3D Viewport Shading to MATERIAL preview
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.clip_end = 1000.0

if __name__ == "__main__":
    print("Generating Complete Solar System 3D Project...")
    build_solar_system()
    out_blend = "/Users/rajkumar/authencation lec18 asd/solar_system.blend"
    bpy.ops.wm.save_as_mainfile(filepath=out_blend)
    print(f"Solar system successfully saved to: {out_blend}")
