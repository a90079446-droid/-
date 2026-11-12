# Korean apartment veranda (meters): narrow room, exterior sliding windows, interior sliding door,
# masked with plastic film, painter in white coverall spraying with a compressor-fed gun.
import bpy, math, sys, random
from mathutils import Vector as V
out = sys.argv[1]; RW, RH, SAMP = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
def M(name, c, r=.6, metal=0, trans=0, alpha=1, coat=0, emit=0, bump=0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = r; b.inputs["Metallic"].default_value = metal
    for k, v in (("Transmission Weight", trans), ("Alpha", alpha), ("Coat Weight", coat)): b.inputs[k].default_value = v
    if emit: b.inputs["Emission Color"].default_value = (*c, 1); b.inputs["Emission Strength"].default_value = emit
    if bump:
        n = m.node_tree.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 160; bp = m.node_tree.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
        m.node_tree.links.new(n.outputs["Fac"], bp.inputs["Height"]); m.node_tree.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m
def box(c, s, m, bev=0.0):
    bpy.ops.mesh.primitive_cube_add(location=c); o = bpy.context.object; o.scale = (s[0] / 2, s[1] / 2, s[2] / 2); o.data.materials.append(m)
    if bev: md = o.modifiers.new("b", "BEVEL"); md.width = bev; md.segments = 3
    return o
def sph(p, r, m, sc_=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=20, radius=r, location=p); o = bpy.context.object; o.scale = sc_; o.data.materials.append(m)
    for q in o.data.polygons: q.use_smooth = True
    return o
def cyl(a, b, r, m, caps=True):
    a, b = V(a), V(b); d = b - a; bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=r, depth=d.length, location=(a + b) / 2)
    o = bpy.context.object; o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = V((0, 0, 1)).rotation_difference(d.normalized()); o.data.materials.append(m)
    for q in o.data.polygons: q.use_smooth = True
    if caps: sph(a, r, m); sph(b, r, m)
    return o
def ik(a, t, l1, l2, pole):
    a, t = V(a), V(t); d = t - a; D = min(d.length, l1 + l2 - 1e-3); u = d.normalized(); x = (l1 * l1 - l2 * l2 + D * D) / (2 * D); h = math.sqrt(max(0, l1 * l1 - x * x))
    pp = (V(pole) - u * V(pole).dot(u)).normalized(); return a + u * x + pp * h, a + u * D
WALL = M("wall", (.93, .92, .88), .9, bump=.05); CEIL = M("ceil", (.97, .97, .95), .9)
TILE = M("tile", (.55, .56, .55), .35, coat=.2); ALU = M("alu", (.88, .9, .92), .35, metal=.6)
GLASS = M("glass", (.8, .9, 1), .05, trans=1.0); FILM = M("film", (.85, .93, 1), .08, trans=1.0); TAPE = M("tape", (1, .85, .1), .5)
SUIT = M("suit", (.96, .96, .97), .85, bump=.12); GRAY = M("gray", (.35, .37, .4), .5); DARK = M("dark", (.03, .03, .035), .4); SKIN = M("skin", (.8, .55, .42), .6)
GLV = M("glove", (.12, .35, .75), .6); BOOT = M("boot", (.06, .05, .04), .5); ORG = M("org", (1, .3, .02), .35, coat=.4); RED = M("red", (.7, .04, .03), .3, coat=1)
# ---- room: x 0..3.4 (along veranda), y 0..1.4 (0 = exterior windows, 1.4 = living-room side), z 0..2.3
LX, LY, LZ = 3.4, 1.4, 2.3
box((LX / 2, LY / 2, -.05), (LX + .4, LY + .4, .1), TILE)                        # floor
box((LX / 2, LY / 2, LZ + .05), (LX + .4, LY + .4, .1), CEIL)                       # ceiling
box((-.05, LY / 2, LZ / 2), (.1, LY + .4, LZ), WALL)                                # end wall (x=0) -> being coated
box((LX + .05, LY / 2, LZ / 2), (.1, LY + .4, LZ), WALL)                            # camera-side wall (open for camera)
# stained wall texture overlay: dark mold patches near corners/ceiling (flat decals)
random.seed(5); MOLD = M("mold", (.04, .05, .03), .9, alpha=.75)
for i in range(16):
    y = random.uniform(.15, 1.25); z = random.choice([random.uniform(1.8, 2.25), random.uniform(.1, .6), random.uniform(.6, 1.8)]); r = random.uniform(.05, .17)
    sph((.003, y, z), r, MOLD, (.01, 1, 1))
# exterior wall y=0: 3 sliding window sashes with plastic masking, city view outside
for k in range(3):
    cx = LX * (k + .5) / 3
    for (c, s) in [((cx, .05, .92), (LX / 3 - .02, .06, .04)), ((cx, .05, 2.0), (LX / 3 - .02, .06, .04)), ((cx - LX / 6 + .02, .05, 1.46), (.04, .06, 1.1)), ((cx + LX / 6 - .02, .05, 1.46), (.04, .06, 1.1))]:
        box(c, s, ALU, .005)
    box((cx, .06, 1.46), (LX / 3 - .06, .01, 1.05), GLASS)
box((LX / 2, .03, .45), (LX, .06, .9), WALL)                                         # parapet below windows
box((LX / 2, .03, 2.15), (LX, .06, .3), WALL)
box((LX / 2, -1.5, 1.4), (30, .1, 14), M("sky", (.55, .75, 1), 1, emit=1.6))         # sky backdrop
for i in range(7): box((random.uniform(-4, 9), -1.2 - random.random(), random.uniform(1.5, 5)), (random.uniform(.8, 1.6), .5, random.uniform(3, 7)), M("bld%d" % i, (.7, .72, .78), .9, emit=.5))
# interior wall y=1.4 with sliding door (masked)
box((LX / 2, LY + .05, LZ / 2), (LX, .1, LZ), WALL)
for (c, s) in [((2.0, LY, 1.1), (1.6, .08, 2.2)), ]:
    pass
box((2.0, LY - .03, 1.1), (1.5, .03, 2.1), M("doorglass", (.75, .85, .95), .05, trans=1))
for (c, s) in [((1.25, LY - .03, 1.1), (.05, .06, 2.15)), ((2.75, LY - .03, 1.1), (.05, .06, 2.15)), ((2.0, LY - .03, 2.15), (1.55, .06, .05)), ((2.0, LY - .03, .05), (1.55, .06, .05)), ((2.0, LY - .03, 1.1), (.04, .07, 2.1))]:
    box(c, s, ALU, .005)
# masking film: floor (rolled out from end wall), windows, door; yellow tape
box((1.4, .7, .012), (2.9, 1.3, .004), FILM)
for k in range(3): box((LX * (k + .5) / 3, .1, 1.46), (LX / 3 - .04, .006, 1.15), FILM)
box((2.0, LY - .06, 1.12), (1.62, .006, 2.22), FILM)
for (c, s) in [((2.0, LY - .06, 2.24), (1.66, .01, .03)), ((1.17, LY - .06, 1.12), (.03, .01, 2.22)), ((2.83, LY - .06, 1.12), (.03, .01, 2.22)), ((1.4, .02, .014), (2.9, .03, .006)), ((.03, .7, .014), (.03, 1.3, .006))]:
    box(c, s, TAPE)
# living room beyond: compressor
cx, cy = 2.1, 2.2
cyl((cx - .28, cy, .28), (cx + .28, cy, .28), .17, RED); box((cx, cy, .62), (.3, .25, .22), M("mot", (.1, .11, .12), .5), .02)
for w in (-.18, .18): cyl((cx + w, cy - .2, .09), (cx + w, cy - .24, .09), .08, DARK, caps=False)
box((.5, 2.6, .2), (1.6, .9, .4), M("sofa", (.4, .5, .6), .8), .06); box((.5, 3.0, .55), (1.6, .2, .5), M("sofa2", (.36, .46, .56), .8), .06)
box((LX / 2, 4, 1.2), (6, .1, 2.6), M("lrw", (.9, .87, .8), .9))
# ---- painter (1.75 m): white disposable coverall, hood, respirator, goggles, boots, gloves
px, py = 1.25, .78
hipZ = .93
def P(dx, dz, dy=0): return V((px + dx, py + dy, dz))
for sy in (-1, 1):
    hip = P(0, hipZ, sy * .1); foot = V((px - .02 + (.1 if sy > 0 else -.05), py + sy * .17, .1)); kn, an = ik(hip, foot, .46, .45, (-1, 0, .1))
    cyl(hip, kn, .085, SUIT); cyl(kn, an, .07, SUIT); sph(an + V((-.06, 0, -.03)), .09, BOOT, (1.8, .8, .6))
cyl(P(0, hipZ + .05), P(0, hipZ + .55), .17, SUIT); cyl(P(0, hipZ + .55), P(0, hipZ + .66), .19, SUIT); cyl(P(0, hipZ + .66), P(0, hipZ + .72), .06, SUIT)
HC = P(-.02, hipZ + .84); sph(HC, .115, SUIT, (1, 1, 1.08))
sph(HC + V((-.085, 0, -.025)), .08, GRAY, (.9, 1.1, .9))                                   # respirator
for sy in (-1, 1): sph(HC + V((-.075, sy * .105, -.035)), .035, DARK, (1.2, .8, .8))   # filter cartridges
cyl(HC + V((-.1, -.115, .035)), HC + V((-.1, .115, .035)), .028, M("goggle", (.1, .25, .35), .1, trans=.6), caps=False)
tip = V((.5, .78, 1.28))
cyl(tip, tip + V((.2, 0, 0)), .014, M("st", (.8, .82, .85), .25, metal=1), caps=False); cyl(tip + V((.18, 0, 0)), tip + V((.42, 0, 0)), .04, ORG)
cyl(tip + V((.3, 0, .04)), tip + V((.3, 0, .16)), .05, M("cup", (.95, .95, .95), .3)); cyl(tip + V((.36, 0, -.02)), tip + V((.4, 0, -.15)), .03, DARK)
grip = tip + V((.38, 0, -.1)); grip2 = tip + V((.52, .03, -.02))
shR = P(0, hipZ + .62, .2); shL = P(0, hipZ + .62, -.2)
for sh, tg, pole in ((shR, grip, (.2, 1, -.5)), (shL, grip2, (.2, -1, -.5))):
    el, en = ik(sh, tg, .3, .28, pole); cyl(sh, el, .052, SUIT); cyl(el, en, .045, SUIT); sph(en, .05, GLV)
# hose: gun -> floor -> door gap -> compressor (orange)
pts = [tip + V((.5, 0, -.1)), tip + V((.6, .05, -.5)), V((1.6, .9, .02)), V((1.9, 1.3, .02)), V((1.95, 1.9, .05)), V((cx, cy - .3, .3))]
cu = bpy.data.curves.new("h", "CURVE"); cu.dimensions = '3D'; sp = cu.splines.new('NURBS'); sp.points.add(len(pts) - 1)
for i, p in enumerate(pts): sp.points[i].co = (*p, 1)
sp.order_u = 4; cu.bevel_depth = .014; cu.resolution_u = 24; ho = bpy.data.objects.new("h", cu); sc.collection.objects.link(ho); ho.data.materials.append(ORG)
# mist + fresh white wall patch
random.seed(2); MIST = M("mist", (.97, .97, .98), .9, alpha=.3, emit=1)
for i in range(120):
    s = random.random(); p = tip.lerp(V((0.01, .78, 1.28)), s); sp_ = .22 * s; p += V((0, random.uniform(-1, 1) * sp_, random.uniform(-1, 1) * sp_)); sph(p, .01 + .03 * s, MIST)
FRESH = M("fresh", (.97, .97, .96), .85, bump=.05); box((.006, .78, 1.2), (.01, 1.1, 1.7), FRESH)
# ---- light & camera
bpy.ops.object.light_add(type='AREA', location=(1.7, .7, 2.25)); c = bpy.context.object; c.data.energy = 220; c.data.size = 1.6; c.rotation_euler = (0, 0, 0)    # ceiling lamp
bpy.ops.object.light_add(type='AREA', location=(1.7, -.6, 1.4)); w = bpy.context.object; w.data.energy = 500; w.data.size = 3; w.rotation_euler = (-math.pi / 2, 0, 0); w.data.color = (.85, .92, 1)  # daylight from the windows
bpy.ops.object.light_add(type='AREA', location=(3.0, 1.0, 1.9)); f = bpy.context.object; f.data.energy = 160; f.data.size = 2; f.rotation_euler = ((V((1.2, .8, 1.2)) - f.location).to_track_quat('-Z', 'Y').to_euler())
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True; wd.node_tree.nodes["Background"].inputs[0].default_value = (.5, .6, .8, 1); wd.node_tree.nodes["Background"].inputs[1].default_value = .4
cd = bpy.data.cameras.new("c"); cd.lens = 24; cd.dof.use_dof = True; cd.dof.aperture_fstop = 4; cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (3.25, 1.15, 1.45); tg = V((.9, .75, 1.2)); cam.rotation_euler = (tg - cam.location).to_track_quat('-Z', 'Y').to_euler(); cd.dof.focus_distance = (tg - cam.location).length
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMP; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 6; sc.cycles.transparent_max_bounces = 8
sc.view_settings.view_transform = 'AgX'; sc.render.resolution_x = RW; sc.render.resolution_y = RH; sc.render.filepath = out
import time; t0 = time.time(); bpy.ops.render.render(write_still=True); print("RENDER_SECONDS", round(time.time() - t0, 1))
