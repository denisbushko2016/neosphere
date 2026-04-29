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

TEMP_AUDIO = OUTPUT_AUDIO / "_temp_Architect_05_v1.wav"
FINAL_VIDEO = OUTPUT_VIDEO / "NeoSphere_Architect_05_v1_FULL.mp4"


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
        carrier_freq=210,
    )

    return binaural, noise, guide


def generate_audio():
    binaural_stages = []
    noise_stages = []
    guide_stages = []

    stages = [
        # 0–2 мин — сбор после холодной ясности
        (120, 300, 12.0, 13.0, 0.08, 0.16, 0.001, 0.004, 0.010, 0.09, 0.11),

        # 2–5 мин — включение действия
        (180, 300, 13.0, 14.0, 0.16, 0.25, 0.004, 0.006, 0.014, 0.11, 0.13),

        # 5–8 мин — устойчивый импульс
        (180, 300, 14.0, 14.5, 0.25, 0.27, 0.006, 0.006, 0.013, 0.13, 0.14),

        # 8–10 мин — фиксация готовности
        (120, 300, 14.5, 13.5, 0.27, 0.20, 0.006, 0.003, 0.009, 0.14, 0.11),
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
    angle = np.arctan2(yv, xv)

    # центральная точка действия
    point_radius = 0.045 - 0.012 * min(progress, 1)
    point = np.exp(-(radius / point_radius) ** 2)

    # направленный лучевой рисунок: импульс наружу
    rays = (0.5 + 0.5 * np.cos(10 * angle - 1.8 * t)) * np.exp(-(radius / 0.85) ** 2)
    rays_strength = max(0, min(1, (progress - 0.18) * 2.5))

    # кольцо запуска
    ring_radius = 0.22 + 0.10 * min(progress, 1)
    ring = np.exp(-((radius - ring_radius) ** 2) / 0.006)
    ring_strength = max(0, min(1, (progress - 0.25) * 2.4))

    # пульсация более активная, чем в Cold Mode
    pulse_rate = 1.45
    pulse_depth = 0.32

    pulse = (1 - pulse_depth) + pulse_depth * (
        0.5 + 0.5 * np.sin(2 * np.pi * pulse_rate * t)
    )

    # финал — чуть спокойнее, чтобы не перевозбудить
    final_stabilize = max(0, min(1, (progress - 0.75) * 4))
    pulse = pulse * (1 - final_stabilize) + 1.0 * final_stabilize

    intensity = (
        0.018 +
        point * 1.15 +
        rays * rays_strength * 0.22 +
        ring * ring_strength * 0.45
    )

    vignette = np.exp(-(radius / 0.78) ** 2)
    intensity = intensity * (0.22 + 0.78 * vignette)
    intensity = intensity * pulse
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

    print(f"[OK] Architect 05 ready: {FINAL_VIDEO}")


if __name__ == "__main__":
    build()
