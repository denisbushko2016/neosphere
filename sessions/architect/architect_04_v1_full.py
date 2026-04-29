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

TEMP_AUDIO = OUTPUT_AUDIO / "_temp_Architect_04_v1.wav"
FINAL_VIDEO = OUTPUT_VIDEO / "NeoSphere_Architect_04_v1_FULL.mp4"


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
        carrier_freq=190,
    )

    return binaural, noise, guide


def generate_audio():
    binaural_stages = []
    noise_stages = []
    guide_stages = []

    stages = [
        # 0–2 мин — отсечение лишнего
        (120, 280, 14.0, 12.5, 0.08, 0.16, 0.001, 0.004, 0.010, 0.12, 0.10),

        # 2–5 мин — холодная ясность
        (180, 280, 12.5, 11.5, 0.16, 0.23, 0.004, 0.006, 0.012, 0.10, 0.085),

        # 5–9 мин — удержание решения
        (240, 280, 11.5, 11.0, 0.23, 0.25, 0.006, 0.006, 0.010, 0.085, 0.075),

        # 9–11 мин — переход к действию
        (120, 280, 11.0, 10.8, 0.25, 0.22, 0.006, 0.004, 0.008, 0.075, 0.07),

        # 11–12 мин — фиксированный выход
        (60, 280, 10.8, 12.0, 0.20, 0.12, 0.004, 0.001, 0.005, 0.07, 0.09),
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

    # почти пустой фон
    background = 0.018

    # холодная центральная точка
    point_radius = 0.045 - 0.010 * min(progress * 1.4, 1)
    point = np.exp(-(radius / point_radius) ** 2)

    # очень тонкое кольцо контроля
    ring_radius = 0.22
    ring_softness = 0.006
    ring = np.exp(-((radius - ring_radius) ** 2) / ring_softness)

    ring_strength = max(0, min(1, (progress - 0.25) * 2.5))

    # микропульс почти незаметный
    pulse_rate = 0.95 - 0.15 * progress
    pulse_depth = 0.18 - 0.08 * progress

    pulse = (1 - pulse_depth) + pulse_depth * (
        0.5 + 0.5 * np.sin(2 * np.pi * pulse_rate * t)
    )

    # финальная стабилизация — меньше движения к концу
    stillness = max(0, min(1, (progress - 0.65) * 3))
    pulse = pulse * (1 - stillness) + 1.0 * stillness

    intensity = (
        background +
        point * 0.92 +
        ring * ring_strength * 0.22
    )

    # периферия почти исчезает
    vignette = np.exp(-(radius / 0.8) ** 2)
    intensity = intensity * (0.22 + 0.78 * vignette)

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

    print(f"[OK] Architect 04 v1 ready: {FINAL_VIDEO}")


if __name__ == "__main__":
    build_full_session()
