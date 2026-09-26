"""Headless motion-graphics render skeleton for Blender 5.x (tested on 5.2.1 LTS, Apple Silicon).

Usage:
  blender -b --factory-startup --python-exit-code 1 -P blender_mg_render.py -- \
      --engine eevee|cycles --rig dolly|path --frames 10 --res 480x270 --fps 30 \
      --samples 32 --out mg_out [--gn] [--gp] [--alpha] [--view 'Khronos PBR Neutral'] [--only 45]

Builds a scene from nothing (no .blend needed), animates the camera with eased keys,
renders a numbered PNG sequence (resumable: existing frames are skipped), logs per-frame
timings as JSON, and saves the .blend next to the frames for inspection.
Encode afterwards with ffmpeg (see the end of this file).
"""
import argparse, json, math, sys, time
from pathlib import Path

import bpy
from bpy_extras import anim_utils
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--engine", default="eevee", choices=["eevee", "cycles"])
ap.add_argument("--rig", default="dolly", choices=["dolly", "path"])
ap.add_argument("--frames", type=int, default=10)
ap.add_argument("--res", default="480x270")
ap.add_argument("--fps", type=int, default=30)
ap.add_argument("--samples", type=int, default=32)
ap.add_argument("--out", default="mg_out")
ap.add_argument("--gn", action="store_true", help="add a Geometry Nodes wave grid")
ap.add_argument("--gp", action="store_true", help="add a Grease Pencil v3 ring")
ap.add_argument("--alpha", action="store_true", help="transparent film (RGBA PNG)")
ap.add_argument("--view", default="Khronos PBR Neutral", help="'Khronos PBR Neutral' (keeps brand colors) | 'AgX' | 'Standard' | 'ACES 2.0'")
ap.add_argument("--only", type=int, default=0, help="render just this frame (look tests)")
args = ap.parse_args(argv)
W, H = map(int, args.res.lower().split("x"))
OUT = Path(args.out); OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- scene reset
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, args.frames
sc.render.fps = args.fps
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.resolution_percentage = 100


def mat(name, color, rough=0.5, metal=0.0, emit=0.0):
    m = bpy.data.materials.new(name)
    # use_nodes is always on in 5.x (the property is deprecated); just edit the tree.
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*color, 1)
        b.inputs["Emission Strength"].default_value = emit
    return m


def link(o):
    sc.collection.objects.link(o)
    return o


def ease_keys(obj, interpolation="BEZIER", easing="AUTO"):
    """Blender 5.x: Action.fcurves is gone (slotted actions). Go through the channelbag."""
    ad = obj.animation_data
    cb = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
    for fc in cb.fcurves:
        for k in fc.keyframe_points:
            k.interpolation = interpolation  # BEZIER (auto-clamped = ease in/out), SINE, EXPO, BACK...
            k.easing = easing                # EASE_IN / EASE_OUT / EASE_IN_OUT for the Penner types
            k.handle_left_type = k.handle_right_type = "AUTO_CLAMPED"
        fc.update()


# ---------------------------------------------------------------- world + look
world = bpy.data.worlds.new("World"); sc.world = world
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.012, 0.014, 0.02, 1)
bg.inputs["Strength"].default_value = 1.0
sc.view_settings.view_transform = args.view            # 'AgX' | 'Khronos PBR Neutral' | 'ACES 2.0' | 'Standard'
if args.view == "AgX":
    sc.view_settings.look = "AgX - Medium High Contrast"
sc.render.film_transparent = args.alpha

# ---------------------------------------------------------------- content
bpy.ops.mesh.primitive_plane_add(size=40)
fl = bpy.context.object; fl.data.materials.append(mat("Floor", (0.02, 0.022, 0.03), rough=0.35))

txt = bpy.data.curves.new("Title", "FONT")
txt.body = "MOTION"; txt.align_x = "CENTER"; txt.align_y = "CENTER"
txt.extrude = 0.08; txt.bevel_depth = 0.012; txt.size = 1.2
title = link(bpy.data.objects.new("Title", txt))
title.location = (0, 0, 1.0); title.rotation_euler = (math.radians(90), 0, 0)
title.data.materials.append(mat("TitleMat", (1.0, 0.45, 0.12), rough=0.25, emit=2.5))

def area(name, loc, power, size, color):
    d = bpy.data.lights.new(name, "AREA"); d.energy = power; d.size = size; d.color = color
    o = link(bpy.data.objects.new(name, d)); o.location = loc
    o.rotation_euler = (Vector((0, 0, 1)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o

area("Key", (4, -5, 5), 600, 4, (1.0, 0.9, 0.8))
area("Rim", (-5, 4, 3), 900, 3, (0.5, 0.7, 1.0))

if args.gn:  # procedural wave grid: pure function of Scene Time -> deterministic per frame
    host = link(bpy.data.objects.new("WaveGrid", bpy.data.meshes.new("WaveGridMesh")))
    ng = bpy.data.node_groups.new("MG_Wave", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = ng.nodes, ng.links
    gi, go = N.new("NodeGroupInput"), N.new("NodeGroupOutput")
    grid = N.new("GeometryNodeMeshGrid")
    grid.inputs["Size X"].default_value = grid.inputs["Size Y"].default_value = 8
    grid.inputs["Vertices X"].default_value = grid.inputs["Vertices Y"].default_value = 28
    pos, t = N.new("GeometryNodeInputPosition"), N.new("GeometryNodeInputSceneTime")
    ln = N.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
    k = N.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = 2.2
    w = N.new("ShaderNodeMath"); w.operation = "MULTIPLY"; w.inputs[1].default_value = 3.0
    ph = N.new("ShaderNodeMath"); ph.operation = "SUBTRACT"
    s = N.new("ShaderNodeMath"); s.operation = "SINE"
    a = N.new("ShaderNodeMath"); a.operation = "MULTIPLY"; a.inputs[1].default_value = 0.25
    xyz = N.new("ShaderNodeCombineXYZ")
    sp = N.new("GeometryNodeSetPosition")
    cube = N.new("GeometryNodeMeshCube"); cube.inputs["Size"].default_value = (0.14, 0.14, 0.14)
    sm = N.new("GeometryNodeSetMaterial"); sm.inputs["Material"].default_value = mat("Cells", (0.2, 0.6, 1.0), rough=0.3, emit=0.6)
    inst = N.new("GeometryNodeInstanceOnPoints")
    L.new(grid.outputs["Mesh"], sp.inputs["Geometry"])
    L.new(pos.outputs["Position"], ln.inputs[0]); L.new(ln.outputs["Value"], k.inputs[0])
    L.new(t.outputs["Seconds"], w.inputs[0]); L.new(k.outputs[0], ph.inputs[0]); L.new(w.outputs[0], ph.inputs[1])
    L.new(ph.outputs[0], s.inputs[0]); L.new(s.outputs[0], a.inputs[0]); L.new(a.outputs[0], xyz.inputs["Z"])
    L.new(xyz.outputs[0], sp.inputs["Offset"])
    L.new(cube.outputs["Mesh"], sm.inputs["Geometry"])
    L.new(sp.outputs["Geometry"], inst.inputs["Points"]); L.new(sm.outputs["Geometry"], inst.inputs["Instance"])
    L.new(inst.outputs["Instances"], go.inputs["Geometry"])
    host.modifiers.new("Wave", "NODES").node_group = ng
    host.location = (0, 3, 0.2)

if args.gp:  # Grease Pencil v3 (4.3+): bpy.data.grease_pencils holds the new type in 5.x
    gpd = bpy.data.grease_pencils.new("Ring")
    layer = gpd.layers.new("Ink")
    drawing = layer.frames.new(1).drawing
    n = 96
    drawing.add_strokes([n + 1])  # closed by a duplicate end point, NOT cyclic=True:
    stroke = drawing.strokes[0]   # a cyclic stroke draws a closing chord during a Build write-on
    for i, p in enumerate(stroke.points):
        ang = 2 * math.pi * i / n
        p.position = (2.1 * math.cos(ang), 0, 2.1 * math.sin(ang))
        p.radius = 0.03
    gm = bpy.data.materials.new("Ink"); bpy.data.materials.create_gpencil_data(gm)
    gm.grease_pencil.color = (1, 1, 1, 1)
    gpd.materials.append(gm)
    ring = link(bpy.data.objects.new("Ring", gpd)); ring.location = (0, 0.3, 1.0)
    build = ring.modifiers.new("WriteOn", "GREASE_PENCIL_BUILD")  # time-based write-on
    build.frame_start, build.length = 1, max(args.frames - 1, 1)

# ---------------------------------------------------------------- camera rig
cd = bpy.data.cameras.new("Cam"); cd.lens = 50; cd.sensor_width = 36
cam = link(bpy.data.objects.new("Cam", cd)); sc.camera = cam
cd.dof.use_dof = True; cd.dof.focus_object = title; cd.dof.aperture_fstop = 2.8
target = link(bpy.data.objects.new("Target", None)); target.location = (0, 0, 1.0)
track = cam.constraints.new("TRACK_TO"); track.target = target
track.track_axis, track.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
f0, f1 = sc.frame_start, sc.frame_end
if args.rig == "dolly":   # one move per shot: slow push-in, eased
    cam.location = (0.6, -9.0, 1.6); cam.keyframe_insert("location", frame=f0)
    cam.location = (0.2, -6.5, 1.3); cam.keyframe_insert("location", frame=f1)
    ease_keys(cam, "BEZIER")
else:                     # arc along a curve with Follow Path, ~22 deg centred on the front (-Y)
    bpy.ops.curve.primitive_bezier_circle_add(radius=8, location=(0, 0, 1.6))
    path = bpy.context.object
    path.rotation_euler.z = math.radians(90)  # probed: offset 0.25 now sits at (0,-8); offsets can't wrap past 0/1
    fp = cam.constraints.new("FOLLOW_PATH"); fp.target = path; fp.use_fixed_location = True
    cam.constraints.move(1, 0)  # Follow Path first, Track To last
    fp.offset_factor = 0.22; cam.keyframe_insert('constraints["Follow Path"].offset_factor', frame=f0)
    fp.offset_factor = 0.28; cam.keyframe_insert('constraints["Follow Path"].offset_factor', frame=f1)
    ease_keys(cam, "SINE", "EASE_IN_OUT")

# ---------------------------------------------------------------- render settings
r = sc.render
r.use_motion_blur = True; r.motion_blur_shutter = 0.5   # 180-degree shutter
r.image_settings.file_format = "PNG"
r.image_settings.color_mode = "RGBA" if args.alpha else "RGB"
r.image_settings.color_depth = "16"                     # 16-bit PNG: dither to 8-bit in ffmpeg, no banding
r.image_settings.compression = 15
if args.engine == "eevee":
    r.engine = "BLENDER_EEVEE"
    e = sc.eevee
    e.taa_render_samples = args.samples
    e.use_raytracing = True; e.ray_tracing_method = "SCREEN"
    e.use_fast_gi = True
    e.use_shadows = True; e.shadow_ray_count = 2
else:
    r.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for backend in ("METAL", "OPTIX", "CUDA", "HIP", "ONEAPI"):  # first GPU backend this build offers
        try:
            prefs.compute_device_type = backend
        except TypeError:
            continue
        prefs.get_devices()
        if any(d.type == backend for d in prefs.devices):
            break
    else:
        prefs.compute_device_type = "NONE"
    gpu = prefs.compute_device_type
    for d in prefs.devices:
        d.use = d.type == gpu                           # GPU only; mixing CPU usually slows Apple Silicon
    c = sc.cycles
    c.device = "GPU" if gpu != "NONE" else "CPU"
    c.samples = args.samples
    c.use_adaptive_sampling = True; c.adaptive_threshold = 0.03
    c.use_denoising = True; c.denoiser = "OPENIMAGEDENOISE"; c.denoising_use_gpu = True
    c.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    c.use_animated_seed = True                          # noise changes per frame -> reads as grain, not a screen door
    c.max_bounces, c.diffuse_bounces, c.glossy_bounces = 6, 2, 2
    c.transparent_max_bounces = 8
    r.use_persistent_data = True                        # keep BVH/shaders between frames

# ---------------------------------------------------------------- render loop (resumable)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "scene.blend"))
log = {"blender": bpy.app.version_string, "engine": r.engine, "res": [W, H], "fps": args.fps,
       "samples": args.samples, "rig": args.rig, "frames": []}
t_all = time.perf_counter()
for f in ([args.only] if args.only else range(f0, f1 + 1)):
    png = OUT / f"{f:04d}.png"
    if png.exists():
        continue
    sc.frame_set(f)
    r.filepath = str(png)
    t = time.perf_counter()
    bpy.ops.render.render(write_still=True)
    log["frames"].append({"frame": f, "sec": round(time.perf_counter() - t, 3)})
log["total_sec"] = round(time.perf_counter() - t_all, 2)
(OUT / "render_log.json").write_text(json.dumps(log, indent=1))
print("MG_RENDER", json.dumps({k: v for k, v in log.items() if k != "frames"}), flush=True)

# Encode (outside Blender). setparams is required: ffmpeg copies the PNG's sRGB transfer tag
# (iec61966-2-1) into the H.264 stream even when -color_trc bt709 is passed.
#   ffmpeg -framerate 30 -i mg_out/%04d.png \
#     -vf "scale=out_color_matrix=bt709:out_range=tv:sws_dither=ed,format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv" \
#     -c:v libx264 -preset slow -crf 18 -tune grain -x264-params aq-mode=3 -movflags +faststart out.mp4
