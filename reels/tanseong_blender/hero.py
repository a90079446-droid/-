# Blender (bpy) hero shot: worker spraying elastic coating with a compressor-fed paint gun.
# usage: python3 hero.py out.png [width height samples]
import bpy, math, sys, random
from mathutils import Vector, Matrix
out = sys.argv[1] if len(sys.argv) > 1 else "hero.png"
RW, RH, SAMP = (int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (540, 960, 32)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
V = Vector

def mat(name, color, rough=0.5, metal=0.0, spec=0.5, coat=0.0, trans=0.0, alpha=1.0, emit=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k, v in (("Coat Weight", coat), ("Transmission Weight", trans), ("Alpha", alpha)):
        if k in b.inputs: b.inputs[k].default_value = v
    if emit and "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = 3
    return m

def smooth(o, sub=2):
    for p in o.data.polygons: p.use_smooth = True
    if sub:
        md = o.modifiers.new("s", "SUBSURF"); md.levels = sub; md.render_levels = sub

def sphere(p, r, m, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=r, location=p)
    o = bpy.context.object; o.scale = scale; o.data.materials.append(m); smooth(o, 0); return o

def cyl_between(a, b, r, m, caps=True):
    a, b = V(a), V(b); d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=r, depth=d.length, location=(a + b) / 2)
    o = bpy.context.object; o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = V((0, 0, 1)).rotation_difference(d.normalized())
    o.data.materials.append(m); smooth(o, 0)
    if caps:
        sphere(a, r * 1.0, m); sphere(b, r * 1.0, m)
    return o

def box(p, s, m, bevel=0.03, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=p); o = bpy.context.object; o.scale = (s[0] / 2, s[1] / 2, s[2] / 2); o.rotation_euler = rot
    o.data.materials.append(m)
    md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 4
    for pl in o.data.polygons: pl.use_smooth = True
    return o

def ik(a, t, l1, l2, pole):
    a, t = V(a), V(t); d = t - a; D = min(d.length, l1 + l2 - 1e-3); u = d.normalized()
    x = (l1 * l1 - l2 * l2 + D * D) / (2 * D); h = math.sqrt(max(0, l1 * l1 - x * x))
    pp = (V(pole) - u * V(pole).dot(u)).normalized()
    return a + u * x + pp * h, a + u * D

# ---------------- materials
SKIN = mat("skin", (1.0, 0.62, 0.42), 0.55)
SHIRT = mat("shirt", (1.0, 0.72, 0.05), 0.6)
OVER = mat("overall", (0.08, 0.22, 0.75), 0.55)
HAT = mat("hat", (1.0, 0.68, 0.02), 0.28, coat=0.35)
GLOVE = mat("glove", (1.0, 0.25, 0.04), 0.5)
BOOT = mat("boot", (0.08, 0.05, 0.03), 0.45)
WHITE = mat("white", (0.95, 0.95, 0.95), 0.4)
STEEL = mat("steel", (0.75, 0.78, 0.82), 0.25, metal=1.0)
ORANGE = mat("orange", (1.0, 0.3, 0.02), 0.35, coat=0.5)
RED = mat("red", (0.75, 0.04, 0.03), 0.3, coat=1.0)
DARK = mat("dark", (0.04, 0.045, 0.05), 0.5)
FLOOR = mat("floor", (0.45, 0.28, 0.14), 0.35, coat=0.3)
PLASTIC = mat("plastic", (0.85, 0.93, 1.0), 0.08, trans=1.0, alpha=1.0)
TAPE = mat("tape", (1.0, 0.85, 0.1), 0.5)

# ---------------- room
WALL_W, WALL_H = 6.4, 5.74
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, WALL_H / 2)); wall = bpy.context.object
wall.scale = (WALL_H, WALL_W, 1); wall.rotation_euler = (0, math.pi / 2, 0)  # plane facing +X
wm = bpy.data.materials.new("wall"); wm.use_nodes = True; nt = wm.node_tree; bsdf = nt.nodes["Principled BSDF"]
tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9; nz.inputs["Detail"].default_value = 8
cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].position = 0.5; cr.color_ramp.elements[1].position = 0.6
sep = nt.nodes.new("ShaderNodeSeparateXYZ"); ob_coord = tc.outputs["Object"]
nt.links.new(ob_coord, mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], cr.color_ramp.inputs[0] if False else cr.inputs["Fac"])
mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = 'RGBA'
mixc.inputs["B"].default_value = (0.03, 0.04, 0.02, 1); mixc.inputs["A"].default_value = (0.9, 0.88, 0.82, 1)
# clean (sprayed) region on one side: mask by object-space Y
nt.links.new(cr.outputs["Color"], mixc.inputs["Factor"])
nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
clean = nt.nodes.new("ShaderNodeMath"); clean.operation = 'LESS_THAN'; clean.inputs[1].default_value = 0.15
nt.links.new(sep.outputs["Y"], clean.inputs[0])
inv = nt.nodes.new("ShaderNodeMath"); inv.operation = 'MULTIPLY'
nt.links.new(cr.outputs["Color"], inv.inputs[0]); inv.inputs[1].default_value = 1.0
f2 = nt.nodes.new("ShaderNodeMath"); f2.operation = 'MULTIPLY'; nt.links.new(inv.outputs[0], f2.inputs[0])
inv2 = nt.nodes.new("ShaderNodeMath"); inv2.operation = 'SUBTRACT'; inv2.inputs[0].default_value = 1.0; nt.links.new(clean.outputs[0], inv2.inputs[1])
nt.links.new(inv2.outputs[0], f2.inputs[1]); nt.links.new(f2.outputs[0], mixc.inputs["Factor"])
nt.links.new(mixc.outputs["Result"], bsdf.inputs["Base Color"]); bsdf.inputs["Roughness"].default_value = 0.85
bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08
nz2 = nt.nodes.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 90
nt.links.new(nz2.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
wall.data.materials.append(wm)
bpy.ops.mesh.primitive_plane_add(size=40, location=(8, 0, 0)); fl = bpy.context.object; fl.data.materials.append(FLOOR)
box((0.08, 0, 0.18), (0.16, WALL_W + .2, 0.36), WHITE, 0.02)   # baseboard
# sash + plastic (side)
SZ = -4.3 * -1  # three z=-4.3 -> blender y=+4.3
for (c, s) in [((3.3, 4.3, 0.1), (.3, 5.7, .2)), ((3.3, 4.3, 4.9), (.3, 5.7, .2)), ((3.3, 4.3 - 2.7, 2.45), (.3, .2, 4.9)), ((3.3, 4.3 + 2.7, 2.45), (.3, .2, 4.9)), ((3.3, 4.3, 2.45), (.26, .14, 4.9))]:
    box(c, s, WHITE, 0.02)
bpy.ops.mesh.primitive_plane_add(size=1, location=(3.3, 4.12, 2.55)); sh = bpy.context.object; sh.scale = (5.7, 5.0, 1); sh.rotation_euler = (math.pi / 2, 0, 0)
sh.rotation_euler = (math.pi / 2, 0, 0); sh.data.materials.append(PLASTIC)
for (c, s) in [((3.3, 4.12, 4.95), (5.8, .04, .12)), ((3.3 - 2.9, 4.12, 2.5), (.12, .04, 5.0)), ((3.3 + 2.9, 4.12, 2.5), (.12, .04, 5.0))]:
    box(c, s, TAPE, 0.005)
# living room + compressor behind plastic
box((3.3, 10, 4), (14, .2, 8), mat("rw", (0.9, 0.86, 0.78), 0.9), 0.0)
box((0.9, 8.6, 0.5), (3.2, 1.2, 1.0), mat("sofa", (0.4, 0.5, 0.65), 0.8), 0.15)
box((0.9, 9.1, 1.2), (3.2, .35, 1.1), mat("sofa2", (0.35, 0.45, 0.6), 0.8), 0.15)
cx, cy = 3.7, 6.9
cyl_between((cx - .85, cy, .95), (cx + .85, cy, .95), .5, RED)
box((cx + .2, cy, 1.75), (.8, .9, .7), DARK, 0.06)
for wx in (-.55, .55): cyl_between((cx + wx, cy - .65, .3), (cx + wx, cy - .8, .3), .28, DARK, caps=False)
sphere((cx - .55, cy - .55, 1.7), .2, WHITE, (1, .4, 1))

# ---------------- worker (Blender coords: facing -X)
CS = 0.95
rx, ry = 2.65, -0.15
hipZ = 1.45
def P(dx, dz, dy=0): return V((rx + dx, ry + dy, dz))   # dx: toward viewer (+x), dy lateral
# torso
cyl_between(P(0, hipZ + .1), P(0, hipZ + .75 * CS), .52 * CS, OVER)
cyl_between(P(0, hipZ + .85 * CS), P(0, hipZ + 1.45 * CS), .47 * CS, SHIRT)
box(P(-.4 * CS, hipZ + 1.0 * CS), (.18 * CS, .7 * CS, .55 * CS), OVER, 0.03)
# head (turned ~100 deg toward the camera, cartoon "looking at us while working")
HC = P(-.05, hipZ + 2.3 * CS)
YAW = math.radians(100)
def R(v):
    c, sn = math.cos(YAW), math.sin(YAW); return V((v.x * c - v.y * sn, v.x * sn + v.y * c, v.z))
def HP(dx, dy, dz): return HC + R(V((dx * CS, dy * CS, dz * CS)))
sphere(HC, .86 * CS, SKIN)
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=.93 * CS, location=HC + V((0, 0, .2 * CS)))
hat = bpy.context.object; hat.scale = (1, 1, .9); hat.data.materials.append(HAT); smooth(hat, 0)
cyl_between(HC + V((0, 0, .12 * CS)), HC + V((0, 0, .17 * CS)), 1.03 * CS, HAT, caps=False)
vb = box(HP(-.8, 0, .2), (.55 * CS, .95 * CS, .08 * CS), HAT, 0.02); vb.rotation_euler = (0, 0, YAW)
for sy in (-1, 1):
    e = sphere(HP(-.74, sy * .3, 0), .19 * CS, WHITE, (.5, 1, 1)); e.rotation_euler = (0, 0, YAW)
    sphere(HP(-.86, sy * .3, 0), .1 * CS, DARK)
    sphere(HP(-.68, sy * .52, -.3), .13 * CS, mat("blush", (1, .45, .4), .6), (.4, 1, .7))
sphere(HP(-.86, 0, -.12), .11 * CS, mat("nose", (.95, .55, .35), .6))
sm = bpy.data.curves.new("smile", "CURVE"); sm.dimensions = '3D'; spn = sm.splines.new('POLY'); spn.points.add(8)
for i in range(9):
    a_ = -0.9 + i * 0.225; spn.points[i].co = (*HP(-.86, math.sin(a_) * .26, -.28 - (math.cos(a_) - 1) * .15), 1)
sm.bevel_depth = .03 * CS; so = bpy.data.objects.new("smile", sm); sc.collection.objects.link(so); so.data.materials.append(mat("lip", (.45, .1, .05), .5))
# legs (crouch): knees forward (-x)
for sy in (-1, 1):
    hip = P(0, hipZ, sy * .3 * CS); foot = V((rx - .15, ry + sy * .5, .3 * CS))
    kn, an = ik(hip, foot, 1.0 * CS, 1.0 * CS, (-1, 0, .1))
    cyl_between(hip, kn, .26 * CS, OVER); cyl_between(kn, an, .24 * CS, OVER)
    sphere(an + V((-.22 * CS, 0, -.1 * CS)), .3 * CS, BOOT, (1.6, .8, .7))
# gun + hands
tip = V((1.35, 0.5, 3.1)); gdir = V((-1, 0, 0))
cyl_between(tip + V((.25, 0, 0)), tip + V((.55, 0, 0)), .08, STEEL, caps=False)
cyl_between(tip + V((.5, 0, 0)), tip + V((1.5, 0, 0)), .24, ORANGE)
cyl_between(tip + V((1.1, 0, .2)), tip + V((1.1, 0, .75)), .3, WHITE)
cyl_between(tip + V((1.1, 0, .75)), tip + V((1.1, 0, .85)), .32, DARK, caps=False)
cyl_between(tip + V((1.3, 0, -.1)), tip + V((1.45, 0, -.7)), .16, DARK)
grip = tip + V((1.4, 0, -.45)); grip2 = tip + V((1.95, 0.1, -.3))
shR = P(0, hipZ + 1.55 * CS, .64 * CS); shL = P(0, hipZ + 1.55 * CS, -.64 * CS)
for sh, tg, pole in ((shR, grip, (.3, 1, -.6)), (shL, grip2, (.3, -1, -.6))):
    el, en = ik(sh, tg, 1.0 * CS, 1.0 * CS, pole)
    sphere(sh, .24 * CS, SHIRT); cyl_between(sh, el, .2 * CS, SHIRT); cyl_between(el, en, .17 * CS, SKIN); sphere(en, .27 * CS, GLOVE)
# hose: from gun rear -> floor -> through sash gap -> compressor
from mathutils import Vector as Vc
pts = [tip + V((1.75, 0, -.35)), tip + V((2.1, .1, -1.0)), V((2.9, .3, .08)), V((2.2, 1.6, .08)), V((1.4, 3.2, .08)), V((1.2, 4.4, .08)), V((1.1, 5.8, .5)), V((3.0, 6.3, 1.0))]
cu = bpy.data.curves.new("hose", "CURVE"); cu.dimensions = '3D'; sp = cu.splines.new('NURBS'); sp.points.add(len(pts) - 1)
for i, p in enumerate(pts): sp.points[i].co = (*p, 1)
sp.order_u = 4; cu.bevel_depth = 0.075; cu.bevel_resolution = 6; cu.resolution_u = 24
ho = bpy.data.objects.new("hose", cu); sc.collection.objects.link(ho); ho.data.materials.append(ORANGE)
# spray mist
random.seed(3)
mm = mat("mist", (0.97, 0.97, 0.98), 0.9, alpha=0.35, emit=(1, 1, 1))
for i in range(110):
    s = random.random(); p = tip.lerp(V((0.02, 0.5 + random.uniform(-.1, .1), 3.1)), s)
    sp_ = 0.5 * s; p += V((0, random.uniform(-1, 1) * sp_, random.uniform(-1, 1) * sp_))
    sphere(p, 0.04 + 0.1 * s, mm)
# sprayed wall already fresh-white where mist lands (handled by wall mask)

# ---------------- lighting & camera
bpy.ops.object.light_add(type='AREA', location=(6, -4, 7)); k = bpy.context.object; k.data.energy = 900; k.data.size = 5; k.rotation_euler = (math.radians(55), math.radians(20), math.radians(50))
bpy.ops.object.light_add(type='AREA', location=(-1, 6, 6)); f = bpy.context.object; f.data.energy = 300; f.data.size = 6; f.data.color = (.8, .9, 1)
bpy.ops.object.light_add(type='AREA', location=(5, 5, 4)); r = bpy.context.object; r.data.energy = 250; r.data.color = (1, .85, .6); r.data.size = 3
for l in (k, f, r):
    d = V((1.3, 0.6, 2.2)) - l.location; l.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.09, 0.12, 0.2, 1); bg.inputs[1].default_value = 0.9
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 50; cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = 5.6
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (15.5, -13.5, 8.0); target = V((1.6, 0.6, 2.3))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam_d.dof.focus_distance = (target - cam.location).length
# ---------------- render
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMP
sc.cycles.use_denoising = True
try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
sc.cycles.max_bounces = 6; sc.cycles.transparent_max_bounces = 8
sc.view_settings.view_transform = 'AgX' if 'AgX' in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items.keys() else 'Filmic'
sc.render.resolution_x = RW; sc.render.resolution_y = RH; sc.render.resolution_percentage = 100
sc.render.filepath = out; sc.render.image_settings.file_format = 'PNG'
import time; t0 = time.time(); bpy.ops.render.render(write_still=True); print("RENDER_SECONDS", round(time.time() - t0, 1))
