# frames_to_gif.py
import os
import imageio

# Pfad zum Ordner mit den Frames
frames_folder = "render"  # Ordner, in dem die PNG-Frames gespeichert sind
output_gif = "output_animation.gif"  # Name der Ausgabe-GIF-Datei
output_mp4 = "double_slit.mp4"  # Name der Ausgabe-MP4-Datei

# Lade alle Frames
frames = []
for filename in sorted(os.listdir(frames_folder)):
    if filename.endswith(".png"):
        filepath = os.path.join(frames_folder, filename)
        frames.append(imageio.imread(filepath))

imageio.mimsave(output_mp4, frames, fps=30, format="FFMPEG", codec="libx264")  # MP4-Video mit 60 FPS
# Speichere als GIF
# imageio.mimsave(output_gif, frames, duration=0.0166666666)  # duration = Zeit pro Frame in Sekunden

print(f"GIF erfolgreich erstellt: {output_gif}")