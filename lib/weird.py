import base64
import subprocess

def b64toWav(data_uri: str, folder: str):
    # Step 1: Decode base64 from data URI
    _, encoded = data_uri.split(",", 1)
    audio_bytes = base64.b64decode(encoded)

    # Step 2: Write WEBM bytes to file
    with open(f"{folder}\\input.webm", "wb") as f:
        f.write(audio_bytes)

    # Step 3: Use ffmpeg via subprocess
    subprocess.run(["C:\\ffmpeg\\bin\\ffmpeg.exe", "-y", "-i", f"{folder}\\input.webm", f"{folder}\\output.wav"], check=True)

    print("Conversion complete: output.wav")