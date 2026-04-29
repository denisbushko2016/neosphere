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

TEMP_AUDIO = OUTPUT_AUDIO / "_temp_Reset_03_v1.wav"
FINAL_VIDEO = OUTPUT_VIDEO / "NeoSphere_Reset_03_v1_FULL.mp4"


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
        carrier_freq=80,
    )

    return binaural, noise, guide


def generate_audio():
    binaural_stages = []
    noise_stages = []
    guide_stages = []

    stages = [
        # 0–2 мин — быстрое снижение внешней активности
        (120, 190, 10.0, 7.0, 0.07, 0.20, 0.006, 0.020, 0.006, 0.035, 0.025),

        # 2–5 мин — глубокое схлопывание перегруза
        (180, 190, 7.0, 4.8, 0.20, 0.24, 0.020, 0.030, 0.005, 0.025, 0.018),

        # 5–8 мин — удержание низкой активности
        (180, 190, 4.8, 4.2, 0.24, 0.20, 0.030, 0.024, 0.004, 0.018, 0.014),

        # 8–10 мин — мягкая стабилизация
        (120, 190, 4.2, 5.5, 0.20, 0.14, 0.024, 0.012, 0.003, 0.014, 0.018),
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

    # эффект аварийного схлопывания: поле постепенно сжимается к центру
    collapse = max(0, min(1, progress * 1.4))

    outer_field = np.exp(-(radius / (0.85 - 0.28 * collapse)) ** 2)
    inner_sink = np.exp(-(radius / (0.36 - 0.10 * collapse)) ** 2)

    # очень медленная, тяжёлая пульсация
    pulse_rate = 0.045
    pulse = 0.72 + 0.28 * np.sin(2 * np.pi * pulse_rate * t)

    # затемнение краёв — ощущение отключения внешнего
    vignette = np.exp(-(radius / 0.82) ** 2)

    # к концу меньше яркости, больше "тишины"
    end_dim = 1.0 - 0.28 * max(0, min(1, (progress - 0.65) * 2.8))

    intensity = (
        0.025 +
        outer_field * 0.45 +
        inner_sink * 0.42
    )

    intensity = intensity * (0.28 + 0.72 * vignette)
    intensity = intensity * pulse
    intensity = intensity * end_dim

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

    print(f"[OK] Reset 03 ready: {FINAL_VIDEO}")


if __name__ == "__main__":
    build()
