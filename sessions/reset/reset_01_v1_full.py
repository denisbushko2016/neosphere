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

TEMP_AUDIO = OUTPUT_AUDIO / "_temp_Reset_01_v1.wav"
FINAL_VIDEO = OUTPUT_VIDEO / "NeoSphere_Reset_01_v1_FULL.mp4"


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
        carrier_freq=110,
    )

    return binaural, noise, guide


def generate_audio():
    binaural_stages = []
    noise_stages = []
    guide_stages = []

    stages = [
        # 0:00–2:00 — вход
        (120, 220, 10.0, 9.1, 0.035, 0.095, 0.001, 0.006, 0.0025, 0.035, 0.030),

        # 2:00–5:00 — погружение
        (180, 220, 9.1, 7.2, 0.095, 0.215, 0.006, 0.014, 0.0045, 0.030, 0.025),

        # 5:00–9:00 — плато
        (240, 220, 7.2, 6.9, 0.215, 0.205, 0.014, 0.014, 0.0025, 0.025, 0.023),

        # 9:00–11:00 — удержание
        (120, 220, 6.9, 6.6, 0.205, 0.150, 0.014, 0.009, 0.002, 0.023, 0.022),

        # 11:00–12:00 — выход
        (60, 220, 6.6, 8.0, 0.110, 0.050, 0.007, 0.001, 0.001, 0.022, 0.030),
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
    # медленная видимая пульсация
    pulse_freq = 0.75
    pulse = 0.55 + 0.45 * np.sin(2 * np.pi * pulse_freq * t)

    # дыхание светового поля
    breath_freq = 0.055
    radius_scale = 0.52 + 0.12 * np.sin(2 * np.pi * breath_freq * t)

    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    xv, yv = np.meshgrid(x, y)

    radius = np.sqrt(xv**2 + yv**2)
    core = np.exp(-(radius / radius_scale) ** 2)

    background = 0.035
    intensity = background + core * pulse * 0.82
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

    print(f"[OK] Final session saved: {FINAL_VIDEO}")


if __name__ == "__main__":
    build_full_session()
