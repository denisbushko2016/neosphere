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

TEMP_AUDIO = OUTPUT_AUDIO / "_temp_Architect_04_v2.wav"
FINAL_VIDEO = OUTPUT_VIDEO / "NeoSphere_Architect_04_v2_FULL.mp4"


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
        carrier_freq=200,
    )

    return binaural, noise, guide


def generate_audio():
    binaural_stages = []
    noise_stages = []
    guide_stages = []

    stages = [
        (120, 300, 14.5, 13.0, 0.10, 0.18, 0.001, 0.003, 0.015, 0.14, 0.12),
        (180, 300, 13.0, 12.0, 0.18, 0.26, 0.003, 0.005, 0.018, 0.12, 0.10),
        (240, 300, 12.0, 11.5, 0.26, 0.28, 0.005, 0.005, 0.016, 0.10, 0.09),
        (120, 300, 11.5, 11.2, 0.28, 0.24, 0.005, 0.004, 0.012, 0.09, 0.08),
        (60, 300, 11.2, 12.5, 0.22, 0.14, 0.004, 0.001, 0.008, 0.08, 0.10),
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

    # --- СИЛЬНАЯ ЦЕНТРАЛЬНАЯ ТОЧКА ---
    point_radius = 0.040 - 0.012 * min(progress, 1)
    point = np.exp(-(radius / point_radius) ** 2)

    # --- ЯРКИЙ ОРЕОЛ ---
    glow_radius = 0.18
    glow = np.exp(-(radius / glow_radius) ** 2)

    # --- ЧЕТКОЕ КОЛЬЦО ---
    ring_radius = 0.26
    ring = np.exp(-((radius - ring_radius) ** 2) / 0.004)

    ring_strength = max(0, min(1, (progress - 0.2) * 2.5))

    # --- ПУЛЬС (четкий, но не дерганый) ---
    pulse_rate = 1.2
    pulse_depth = 0.35

    pulse = (1 - pulse_depth) + pulse_depth * (
        0.5 + 0.5 * np.sin(2 * np.pi * pulse_rate * t)
    )

    # --- СОСТАВ ---
    intensity = (
        0.02 +
        point * 1.2 +
        glow * 0.9 +
        ring * ring_strength * 0.5
    )

    # затемнение периферии
    vignette = np.exp(-(radius / 0.7) ** 2)
    intensity = intensity * (0.2 + 0.8 * vignette)

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

    print(f"[OK] Architect 04 v2 ready: {FINAL_VIDEO}")


if __name__ == "__main__":
    build_full_session()
