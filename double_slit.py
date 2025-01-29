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
frames = 100
wavelength = 0.5

# ---------- Material Setup ----------
mat = bpy.data.materials.new(name="WaveMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.2, 0.4, 1.0, 1.0)
bsdf.inputs["Metallic"].default_value = 0.3


# ---------- Wellenfunktion ----------
def psi(x, y, t):
    if -0.3 < x < 0.3 and (abs(y) > 0.7 or abs(y) < 0.4):
        return 0.0
    r = np.sqrt((x + 2 * t) ** 2 + y ** 2)
    return np.exp(-0.25 * (r - 3 * t) ** 2) * np.sin(2 * np.pi * r / wavelength)


# ---------- Animation ----------
for frame in range(frames):
    # Entferne vorheriges Objekt korrekt
    for obj in coll.objects:
        if obj.name.startswith("WaveObject"):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Erstelle Vertices und Faces
    verts = []
    faces = []

    for i in range(N):
        for j in range(N):
            x = (i / N - 0.5) * 10
            y = (j / N - 0.5) * 10
            z = abs(psi(x, y, frame / 10)) ** 2  # Skalierung verbessert
            verts.append((x, y, z))

    for i in range(N - 1):
        for j in range(N - 1):
            idx = i * N + j
            faces.append([idx, idx + 1, idx + N + 1, idx + N])

    # Mesh erstellen
    mesh = bpy.data.meshes.new("WaveMesh")
    mesh.from_pydata(verts, [], faces)  # Faces hinzugefügt
    obj = bpy.data.objects.new("WaveObject", mesh)
    coll.objects.link(obj)

    obj.data.materials.append(mat)  # Material korrekt zuweisen

    # Subdivision Surface Modifier hinzufügen
    modifier = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    modifier.levels = 3

    # Shade Smooth aktivieren
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()

    # Render-Einstellungen
    bpy.context.scene.frame_set(frame)
    bpy.context.scene.render.filepath = f"//render/frame_{frame:04d}.png"
    bpy.ops.render.render(write_still=True, use_viewport=True)
