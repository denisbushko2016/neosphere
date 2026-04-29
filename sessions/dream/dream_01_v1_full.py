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

TEMP_AUDIO = OUTPUT_AUDIO / "_temp_Dream_01_v1.wav"
FINAL_VIDEO = OUTPUT_VIDEO / "NeoSphere_Dream_01_v1_FULL.mp4"


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
        carrier_freq=90,
    )

    return binaural, noise, guide


def generate_audio():
    binaural_stages = []
    noise_stages = []
    guide_stages = []

    stages = [
        # 0–3 мин — снижение активности
        (180, 210, 8.5, 7.2, 0.045, 0.12, 0.004, 0.012, 0.004, 0.030, 0.024),

        # 3–7 мин — потеря линейного фокуса
        (240, 210, 7.2, 5.8, 0.12, 0.18, 0.012, 0.020, 0.006, 0.024, 0.018),

        # 7–12 мин — образное поле
        (300, 210, 5.8, 4.5, 0.18, 0.16, 0.020, 0.018, 0.004, 0.018, 0.014),
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

    # медленное образное поле
    wave1 = np.sin(2.2 * xv + 0.35 * t)
    wave2 = np.sin(2.0 * yv + 0.28 * t)
    wave3 = np.sin(2.6 * (xv + yv) + 0.22 * t)

    dream_field = (wave1 + wave2 + wave3) / 3
    dream_field = np.exp(-(dream_field ** 2))

    # центр не фиксирует внимание, а мягко растворяет его
    soft_center = np.exp(-(radius / 0.78) ** 2)

    # медленное дыхание яркости
    breath = 0.72 + 0.28 * np.sin(2 * np.pi * 0.055 * t)

    # чем дальше, тем меньше контраста и больше "плывучести"
    contrast = 0.42 - 0.18 * progress

    # лёгкая периферийная темнота
    vignette = np.exp(-(radius / 0.95) ** 2)

    intensity = (
        0.035 +
        soft_center * 0.42 +
        dream_field * contrast
    )

    intensity = intensity * (0.45 + 0.55 * vignette)
    intensity = intensity * breath

    # мягкое затемнение к концу, чтобы не бодрить
    end_dim = 1.0 - 0.18 * max(0, min(1, (progress - 0.75) * 4))
    intensity = intensity * end_dim

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

    print(f"[OK] Dream 01 v1 ready: {FINAL_VIDEO}")


if __name__ == "__main__":
    build_full_session()
