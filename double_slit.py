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
frames = 200
wavelength = 1
slit_width = 0.2
slit_separation = 2

# ---------- Barriere erstellen ----------
# Berechnung der Spaltgrenzen
lower_bound = -slit_separation / 2 - slit_width / 2
upper_bound = slit_separation / 2 + slit_width / 2

height = 0.1

# Vertices für die drei Wandteile
vertices = [
    # Unterer Block (y < -slit_separation/2 - slit_width/2)
    (-0.3, -5, 0), (0.3, -5, 0),
    (0.3, lower_bound, 0), (-0.3, lower_bound, 0),
    # unterer block aber oberteil
    (-0.3, -5, height), (0.3, -5, height),
    (0.3, lower_bound, height), (-0.3, lower_bound, height),

    # Mittlerer Block (zwischen den Spalten)
    (-0.3, -slit_separation / 2 + slit_width / 2, 0),
    (0.3, -slit_separation / 2 + slit_width / 2, 0),
    (0.3, slit_separation / 2 - slit_width / 2, 0),
    (-0.3, slit_separation / 2 - slit_width / 2, 0),
    # mittlerer block aber oberteil
    (-0.3, -slit_separation / 2 + slit_width / 2, height),
    (0.3, -slit_separation / 2 + slit_width / 2, height),
    (0.3, slit_separation / 2 - slit_width / 2, height),
    (-0.3, slit_separation / 2 - slit_width / 2, height),

    # Oberer Block (y > slit_separation/2 + slit_width/2)
    (-0.3, upper_bound, 0), (0.3, upper_bound, 0),
    (0.3, 5, 0), (-0.3, 5, 0),
    # oberer block aber oberteil
    (-0.3, upper_bound, height), (0.3, upper_bound, height),
    (0.3, 5, height), (-0.3, 5, height)
]

# Faces für die drei Rechtecke
faces = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18, 19], [20, 21, 22, 23]]
faces.extend([[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]])

# Mesh erstellen
mesh = bpy.data.meshes.new("BarrierMesh")
mesh.from_pydata(vertices, [], faces)
barrier = bpy.data.objects.new("Barrier", mesh)
coll.objects.link(barrier)

# Schwarzes Material für die Barriere
mat_barrier = bpy.data.materials.new(name="BarrierMaterial")
mat_barrier.use_nodes = True
bsdf = mat_barrier.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0, 0, 0, 1)
bsdf.inputs["Roughness"].default_value = 0.8
barrier.data.materials.append(mat_barrier)


# ---------- Wellen Parameter ----------
wave_start_x = -4.0
wave_start_y = 0
wave_speed = 2.0

# ---------- Wellen Material ----------
mat_wave = bpy.data.materials.new(name="WaveMaterial")
mat_wave.use_nodes = True
bsdf = mat_wave.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.2, 0.4, 1.0, 1.0)
bsdf.inputs["Metallic"].default_value = 0.3

# ---------- Physikalische Parameter ergänzen ----------
barriere_x = 0  # X-Position der Barriere
t_barriere = (barriere_x - wave_start_x) / wave_speed  # Zeit bis die Welle die Barriere erreicht


# ---------- Wellenfunktion mit instantaner Spaltanregung ----------
# from numba import jit
# @jit(nopython=True)
def psi(x, y, t):
    # Originalwelle (vor der Barriere)
    if x < barriere_x - 0.3:
        dx = x - wave_start_x
        dy = y - wave_start_y
        r = np.sqrt(dx ** 2 + dy ** 2)
        return np.exp(-0.25 * (r - wave_speed * t) ** 2) * np.sin(2 * np.pi * r / wavelength)

    # In der Barriere
    elif barriere_x - 0.3 <= x <= barriere_x + 0.3:
        # Spaltcheck
        in_slit1 = abs(y + slit_separation / 2) < slit_width / 2
        in_slit2 = abs(y - slit_separation / 2) < slit_width / 2

        if not (in_slit1 or in_slit2):
            return 0.0
        else:
            # Amplitude = Originalwelle am Spaltstandort
            slit_x = barriere_x
            slit_y = -slit_separation / 2 if in_slit1 else slit_separation / 2
            dx_slit = slit_x - wave_start_x
            dy_slit = slit_y - wave_start_y
            r_slit = np.sqrt(dx_slit ** 2 + dy_slit ** 2)
            amp = np.exp(-0.25 * (r_slit - wave_speed * t) ** 2)
            phase = 2 * np.pi * r_slit / wavelength

            return amp * np.sin(phase)

    # Hinter der Barriere
    else:
        # Beiträge beider Spalte
        total = 0.0
        for slit_y in [-slit_separation / 2, slit_separation / 2]:
            # Abstand vom Spalt zum aktuellen Punkt
            r_spalt = np.sqrt((x - barriere_x) ** 2 + (y - slit_y) ** 2)

            # Amplitude am Spalt (wie oben berechnet)
            dx_slit = barriere_x - wave_start_x
            dy_slit = slit_y - wave_start_y
            r_slit = np.sqrt(dx_slit ** 2 + dy_slit ** 2)
            amp = np.exp(-0.25 * (r_slit - wave_speed * t) ** 2)

            # Neue Welle vom Spalt aus
            total += amp * np.exp(-0.1 * r_spalt) * np.sin(2 * np.pi * r_spalt / wavelength)

        return total

# ---------- Animation ----------
for frame in range(frames):
    # Alte Wellenobjekte entfernen
    for obj in coll.objects:
        if obj.name.startswith("WaveObject"):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Neue Wellenform berechnen
    verts = []
    for i in range(N):
        for j in range(N):
            x = (i / N - 0.5) * 10
            y = (j / N - 0.5) * 10
            z = abs(psi(x, y, frame / 20)) ** 2 * 1.5
            verts.append((x, y, z))

    # Mesh erstellen
    faces = []
    for i in range(N - 1):
        for j in range(N - 1):
            v1 = i * N + j
            faces.append([v1, v1 + 1, v1 + N + 1, v1 + N])

    mesh = bpy.data.meshes.new("WaveMesh")
    mesh.from_pydata(verts, [], faces)
    obj = bpy.data.objects.new("WaveObject", mesh)
    coll.objects.link(obj)
    obj.data.materials.append(mat_wave)

    # Glättung hinzufügen
    modifier = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    modifier.levels = 6
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()

    # Frame rendern
    bpy.context.scene.frame_set(frame)
    bpy.context.scene.render.filepath = f"//render/frame_{frame:04d}.png"
    bpy.ops.render.render(write_still=True)

# ---------- Render Einstellungen ----------
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720