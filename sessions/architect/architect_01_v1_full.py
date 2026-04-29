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

TEMP_AUDIO = OUTPUT_AUDIO / "_temp_Architect_01_v1.wav"
FINAL_VIDEO = OUTPUT_VIDEO / "NeoSphere_Architect_01_v1_FULL.mp4"


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
        carrier_freq=140,
    )

    return binaural, noise, guide


def generate_audio():
    binaural_stages = []
    noise_stages = []
    guide_stages = []

    stages = [
        # 0–2 мин — вход (очень мягкий)
        (120, 220, 11.5, 10.5, 0.05, 0.12, 0.002, 0.006, 0.006, 0.08, 0.07),

        # 2–5 мин — появление структуры
        (180, 220, 10.5, 9.8, 0.12, 0.20, 0.006, 0.012, 0.010, 0.07, 0.065),

        # 5–9 мин — плато (структурное поле)
        (240, 220, 9.8, 9.4, 0.20, 0.22, 0.012, 0.012, 0.008, 0.065, 0.06),

        # 9–11 мин — стабилизация
        (120, 220, 9.4, 9.1, 0.22, 0.18, 0.012, 0.008, 0.006, 0.06, 0.058),

        # 11–12 мин — мягкий выход
        (60, 220, 9.1, 10.5, 0.16, 0.08, 0.006, 0.002, 0.004, 0.058, 0.07),
    ]

    for params in stages:
        b, n, g = build_raw_stage(*params)
        binaural_stages.append(b)
        noise_stages.append(n)
        guide_stages.append(g)

    full_binaural = concatenate_stages(binaural_stages)
    full_noise = concatenate_stages(noise_stages)
    full_guide = concatenate_stages(guide_stages)

    audio = mix_layers([full_binaural, full_noise, full_guide])
    save_wav(audio, TEMP_AUDIO)

    return sum(stage[0] for stage in stages)


def make_frame(t, duration, width=1080, height=1080):
    progress = t / duration

    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    xv, yv = np.meshgrid(x, y)

    radius = np.sqrt(xv**2 + yv**2)

    # мягкое поле
    field = np.exp(-(radius / 0.75)**2)

    # очень мягкая структура (без жёсткой геометрии)
    structure = (
        np.sin(3 * xv + t * 0.3) +
        np.sin(3 * yv + t * 0.35)
    ) / 2

    structure_strength = max(0, min(1, (progress - 0.2) * 2))

    # лёгкое дыхание (не пульс)
    breath = 0.96 + 0.04 * np.sin(2 * np.pi * 0.08 * t)

    intensity = (
        0.05 +
        field * 0.75 +
        structure * structure_strength * 0.12
    )

    intensity = intensity * breath

    # мягкое затемнение краёв
    vignette = np.exp(-(radius / 0.9)**2)
    intensity = intensity * (0.4 + 0.6 * vignette)

    intensity = np.clip(intensity, 0, 1)

    frame = np.uint8(255 * intensity)
    return np.stack([frame, frame, frame], axis=2)


def build_full_session():
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

    print(f"[OK] Architect 01 v1 ready: {FINAL_VIDEO}")


if __name__ == "__main__":
    build_full_session()
