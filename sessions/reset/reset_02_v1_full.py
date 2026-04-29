import sys
from pathlib import Path
from moviepy.editor import VideoClip, AudioFileClip
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from app.config import LIB_PATH
sys.path.append(str(LIB_PATH))

from core.audio_engine_v2 import (
    generate_binaural_stage,
    generate_noise_stage,
    generate_guiding_layer,
    concatenate_stages,
    mix_layers,
    save_wav,
)

OUTPUT_AUDIO = ROOT / "output" / "audio"
OUTPUT_VIDEO = ROOT / "output" / "video"

TEMP_AUDIO = OUTPUT_AUDIO / "_temp_Reset_02.wav"
FINAL_VIDEO = OUTPUT_VIDEO / "NeoSphere_Reset_02_v1_FULL.mp4"


def generate_audio():
    stages = [
        (240, 200, 9.0, 6.0, 0.06, 0.20, 0.01, 0.03, 0.006, 0.03, 0.02),
        (300, 200, 6.0, 4.0, 0.20, 0.15, 0.03, 0.02, 0.004, 0.02, 0.015),
    ]

    binaural, noise, guide = [], [], []

    for p in stages:
        b = generate_binaural_stage(
            duration_sec=p[0],
            carrier_freq=p[1],
            start_beat=p[2],
            end_beat=p[3],
            volume_start=p[4],
            volume_end=p[5],
        )

        n = generate_noise_stage(
            duration_sec=p[0],
            volume_start=p[6],
            volume_end=p[7],
        )

        g = generate_guiding_layer(
            duration_sec=p[0],
            pulse_start=p[9],
            pulse_end=p[10],
            volume=p[8],
            carrier_freq=90,
        )

        binaural.append(b)
        noise.append(n)
        guide.append(g)

    audio = mix_layers([
        concatenate_stages(binaural),
        concatenate_stages(noise),
        concatenate_stages(guide),
    ])

    save_wav(audio, TEMP_AUDIO)

    return sum(s[0] for s in stages)


def make_frame(t, duration):
    x = np.linspace(-1, 1, 1080)
    y = np.linspace(-1, 1, 1080)
    xv, yv = np.meshgrid(x, y)

    r = np.sqrt(xv**2 + yv**2)

    center = np.exp(-(r / 0.6) ** 2)
    pulse = 0.7 + 0.3 * np.sin(2 * np.pi * 0.06 * t)

    intensity = center * pulse
    intensity = np.clip(intensity, 0, 1)

    frame = np.uint8(255 * intensity)
    return np.stack([frame, frame, frame], axis=2)


def build():
    OUTPUT_AUDIO.mkdir(parents=True, exist_ok=True)
    OUTPUT_VIDEO.mkdir(parents=True, exist_ok=True)

    duration = generate_audio()

    video = VideoClip(lambda t: make_frame(t, duration), duration=duration)

    audio = AudioFileClip(str(TEMP_AUDIO))
    video = video.set_audio(audio)

    video.write_videofile(
        str(FINAL_VIDEO),
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    video.close()
    audio.close()

    if TEMP_AUDIO.exists():
        TEMP_AUDIO.unlink()

    print("[OK] Reset 02 ready")


if __name__ == "__main__":
    build()
