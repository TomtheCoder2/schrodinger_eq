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
frames = 3
wavelength = 0.5
slit_width = 0.6  # Breite jedes Spalts
slit_separation = 2.5  # Abstand zwischen Spaltmitten

# ---------- Material Setup ----------
mat = bpy.data.materials.new(name="WaveMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.2, 0.4, 1.0, 1.0)
bsdf.inputs["Metallic"].default_value = 0.3


# ---------- Wellenfunktion mit 2 Spalten ----------
def psi(x, y, t):
    # Barriere mit 2 Spalten
    if -0.3 < x < 0.3:
        # Spaltpositionen
        slit1 = (y > -slit_separation / 2 - slit_width / 2) and (y < -slit_separation / 2 + slit_width / 2)
        slit2 = (y > slit_separation / 2 - slit_width / 2) and (y < slit_separation / 2 + slit_width / 2)
        if not (slit1 or slit2):
            return 0.0

    # Wellenausbreitung
    r = np.sqrt((x + 2 * t) ** 2 + y ** 2)
    return np.exp(-0.25 * (r - 3 * t) ** 2) * np.sin(2 * np.pi * r / wavelength)


# ---------- Animation ----------
for frame in range(frames):
    # Lösche vorheriges Mesh
    for obj in coll.objects:
        if obj.name.startswith("WaveObject"):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Generiere Vertices
    verts = []
    for i in range(N):
        for j in range(N):
            x = (i / N - 0.5) * 10
            y = (j / N - 0.5) * 10
            z = abs(psi(x, y, frame / 10)) ** 2   # Verstärkte Z-Skalierung
            verts.append((x, y, z))

    # Generiere Faces
    faces = []
    for i in range(N - 1):
        for j in range(N - 1):
            v1 = i * N + j
            v2 = v1 + 1
            v3 = v1 + N + 1
            v4 = v1 + N
            faces.append([v1, v2, v3, v4])

    # Erstelle Mesh
    mesh = bpy.data.meshes.new("WaveMesh")
    mesh.from_pydata(verts, [], faces)
    obj = bpy.data.objects.new("WaveObject", mesh)
    coll.objects.link(obj)
    obj.data.materials.append(mat)

    # Optimierte Subdivision
    modifier = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    modifier.levels = 2  # Reduziert für bessere Performance
    modifier.render_levels = 2

    # Glättung
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()

    # Rendern
    bpy.context.scene.frame_set(frame)
    bpy.context.scene.render.filepath = f"//render/frame_{frame:04d}.png"
    bpy.ops.render.render(write_still=True)

# Render-Einstellungen
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720