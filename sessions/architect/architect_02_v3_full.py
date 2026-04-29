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

TEMP_AUDIO = OUTPUT_AUDIO / "_temp_Architect_02_v3.wav"
FINAL_VIDEO = OUTPUT_VIDEO / "NeoSphere_Architect_02_v3_FULL.mp4"


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
        carrier_freq=150,
    )

    return binaural, noise, guide


def generate_audio():
    binaural_stages = []
    noise_stages = []
    guide_stages = []

    stages = [
        # 0–2 мин — мягкий хаос
        (120, 240, 11.0, 10.2, 0.08, 0.16, 0.003, 0.010, 0.010, 0.09, 0.08),

        # 2–5 мин — сбор в центр
        (180, 240, 10.2, 9.4, 0.16, 0.24, 0.010, 0.015, 0.014, 0.08, 0.07),

        # 5–8 мин — проявление структуры
        (180, 240, 9.4, 8.9, 0.24, 0.26, 0.015, 0.015, 0.012, 0.07, 0.065),

        # 8–12 мин — выбор / фиксация
        (240, 240, 8.9, 9.5, 0.26, 0.22, 0.015, 0.010, 0.010, 0.065, 0.08),
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

    # 1. Начальный мягкий хаос: несколько размытых пятен
    noise_field = (
        np.sin(3 * xv + t * 0.5) +
        np.sin(4 * yv + t * 0.6) +
        np.sin(5 * (xv + yv) + t * 0.4)
    ) / 3

    chaos_strength = max(0, min(1, 1 - progress * 2.2))
    chaos = np.exp(-(noise_field**2)) * chaos_strength

    # 2. Схлопывание в центральное светлое поле
    collapse_strength = max(0, min(1, (progress - 0.18) * 3.2))
    center_blob = np.exp(-(radius / 0.62)**2) * collapse_strength

    # 3. Мягкие контуры структуры
    contour_strength = max(0, min(1, (progress - 0.42) * 3))
    contour = np.sin(6 * xv) * np.sin(6 * yv) * contour_strength * 0.14

    # 4. Финальный правильный тёмный круг в ярком поле
    circle_strength = max(0, min(1, (progress - 0.62) * 3.0))

    bright_field = np.exp(-(radius / 0.75)**2) * circle_strength * 0.85

    circle_radius = 0.31
    edge_softness = 0.018

    dark_circle = 1 / (1 + np.exp((radius - circle_radius) / edge_softness))
    dark_circle = dark_circle * circle_strength

    # Пульсация постепенно успокаивается
    pulse_rate = 1.1 - 0.35 * progress
    pulse_depth = 0.42 - 0.20 * progress

    pulse = (1 - pulse_depth) + pulse_depth * (
        0.5 + 0.5 * np.sin(2 * np.pi * pulse_rate * t)
    )

    intensity = (
        0.045 +
        chaos * 0.55 +
        center_blob * 0.62 +
        contour +
        bright_field
    )

    intensity = intensity * (1 - dark_circle * 0.92)
    intensity = intensity * pulse
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

    print(f"[OK] Architect 02 v3 ready: {FINAL_VIDEO}")


if __name__ == "__main__":
    build_full_session()
