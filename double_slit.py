import bpy
import numpy as np

# ---------- Szenen-Setup ----------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

coll = bpy.data.collections.new("Simulation")
bpy.context.scene.collection.children.link(coll)

# ---------- Kamera & Licht ----------
bpy.ops.object.camera_add(location=(0, -15, 8))
camera = bpy.context.object
camera.rotation_euler = (np.radians(60), 0, 0)
bpy.context.scene.camera = camera

bpy.ops.object.light_add(type='SUN', location=(0, -10, 20))
sun = bpy.context.object
sun.data.energy = 5

# ---------- Simulation Parameter ----------
N = 100
frames = 100  # Erhöht für längere Animation
wavelength = 0.5
slit_width = 0.6
slit_separation = 2.5

# NEUE PARAMETER: Wellenstartposition
wave_start_x = -4.0  # Startposition x (links vom Doppelspalt)
wave_start_y = 0  # Startposition y (leicht versetzt)
wave_speed = 2.0  # Ausbreitungsgeschwindigkeit

# ---------- Material Setup ----------
mat = bpy.data.materials.new(name="WaveMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.2, 0.4, 1.0, 1.0)
bsdf.inputs["Metallic"].default_value = 0.3


# ---------- Modifizierte Wellenfunktion ----------
def psi(x, y, t):
    # Barrierebedingung (unverändert)
    if -0.3 < x < 0.3:
        slit1 = (y > -slit_separation / 2 - slit_width / 2) and (y < -slit_separation / 2 + slit_width / 2)
        slit2 = (y > slit_separation / 2 - slit_width / 2) and (y < slit_separation / 2 + slit_width / 2)
        if not (slit1 or slit2):
            return 0.0

    # NEUE BERECHNUNG: Relativ zur Startposition
    dx = x - wave_start_x + wave_speed * t  # Bewegung in +x-Richtung
    dy = y - wave_start_y
    r = np.sqrt(dx ** 2 + dy ** 2)

    return np.exp(-0.25 * (r - 3 * t) ** 2) * np.sin(2 * np.pi * r / wavelength)


# ---------- Animation (unverändert) ----------
for frame in range(frames):
    for obj in coll.objects:
        if obj.name.startswith("WaveObject"):
            bpy.data.objects.remove(obj, do_unlink=True)

    verts = []
    for i in range(N):
        for j in range(N):
            x = (i / N - 0.5) * 10
            y = (j / N - 0.5) * 10
            z = abs(psi(x, y, frame / 10)) ** 2 * 1.5  # Intensität skaliert
            verts.append((x, y, z))

    faces = []
    for i in range(N - 1):
        for j in range(N - 1):
            v1 = i * N + j
            faces.append([v1, v1 + 1, v1 + N + 1, v1 + N])

    mesh = bpy.data.meshes.new("WaveMesh")
    mesh.from_pydata(verts, [], faces)
    obj = bpy.data.objects.new("WaveObject", mesh)
    coll.objects.link(obj)
    obj.data.materials.append(mat)

    modifier = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    modifier.levels = 5

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()

    bpy.context.scene.frame_set(frame)
    bpy.context.scene.render.filepath = f"//render/frame_{frame:04d}.png"
    bpy.ops.render.render(write_still=True)

# Render-Einstellungen
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720