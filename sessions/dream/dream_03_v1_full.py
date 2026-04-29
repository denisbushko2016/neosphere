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

TEMP_AUDIO = OUTPUT_AUDIO / "_temp_Dream_03_v1.wav"
FINAL_VIDEO = OUTPUT_VIDEO / "NeoSphere_Dream_03_v1_FULL.mp4"


def build_raw_stage(duration, carrier, start_beat, end_beat,
                    binaural_start, binaural_end,
                    noise_start, noise_end,
                    guide_volume,
                    guide_pulse_start, guide_pulse_end):

    binaural = generate_binaural_stage(
        duration_sec=duration,
        carrier_freq=carrier,
        start_beat=start_beat,
        end_beat=end_beat,
        volume_start=binaural_start,
        volume_end=binaural_end,
    )

    noise = generate_noise_stage(
        duration_sec=duration,
        volume_start=noise_start,
        volume_end=noise_end,
    )

    guide = generate_guiding_layer(
        duration_sec=duration,
        pulse_start=guide_pulse_start,
        pulse_end=guide_pulse_end,
        volume=guide_volume,
        carrier_freq=65,
    )

    return binaural, noise, guide


def generate_audio():
    binaural_stages = []
    noise_stages = []
    guide_stages = []

    stages = [
        # 0–4 мин — мягкое удержание сонного поля
        (240, 170, 4.2, 3.6, 0.07, 0.13, 0.012, 0.018, 0.003, 0.010, 0.008),

        # 4–10 мин — стабилизация
        (360, 170, 3.6, 3.0, 0.13, 0.14, 0.018, 0.018, 0.0025, 0.008, 0.006),

        # 10–16 мин — глубокое фоновое удержание
        (360, 170, 3.0, 2.8, 0.14, 0.10, 0.018, 0.012, 0.002, 0.006, 0.005),
    ]

    for params in stages:
        b, n, g = build_raw_stage(*params)
        binaural_stages.append(b)
        noise_stages.append(n)
        guide_stages.append(g)

    audio = mix_layers([
        concatenate_stages(binaural_stages),
        concatenate_stages(noise_stages),
        concatenate_stages(guide_stages),
    ])

    save_wav(audio, TEMP_AUDIO)
    return sum(stage[0] for stage in stages)


def make_frame(t, duration, width=1080, height=1080):
    progress = t / duration

    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    xv, yv = np.meshgrid(x, y)

    radius = np.sqrt(xv**2 + yv**2)

    # почти неподвижное сонное поле
    wave1 = np.sin(0.9 * xv + 0.06 * t)
    wave2 = np.sin(0.8 * yv + 0.045 * t)
    wave3 = np.sin(1.0 * (xv + yv) + 0.035 * t)

    field = (wave1 + wave2 + wave3) / 3
    field = np.exp(-(field ** 2))

    center = np.exp(-(radius / 1.05) ** 2)

    # очень слабое дыхание
    breath = 0.58 + 0.14 * np.sin(2 * np.pi * 0.022 * t)

    # постепенное исчезновение картинки
    dim = 1.0 - 0.48 * progress

    # почти полное снижение контраста к концу
    contrast = 0.24 - 0.12 * progress

    vignette = np.exp(-(radius / 1.05) ** 2)

    intensity = (
        0.018 +
        center * 0.24 +
        field * contrast
    )

    intensity = intensity * (0.40 + 0.60 * vignette)
    intensity = intensity * breath
    intensity = intensity * dim

    intensity = np.clip(intensity, 0, 1)

    frame = np.uint8(255 * intensity)
    return np.stack([frame, frame, frame], axis=2)


def build():
    OUTPUT_AUDIO.mkdir(parents=True, exist_ok=True)
    OUTPUT_VIDEO.mkdir(parents=True, exist_ok=True)

    duration = generate_audio()

    video = VideoClip(
        lambda t: make_frame(t, duration),
        duration=duration
    )

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

    print(f"[OK] Dream 03 ready: {FINAL_VIDEO}")


if __name__ == "__main__":
    build()
