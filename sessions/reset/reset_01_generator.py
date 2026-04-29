import sys
from pathlib import Path

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


def generate_reset_01_v3():
    binaural_stages = []
    noise_stages = []
    guide_stages = []

    # 0:00–2:00 — вход: почти незаметный фон
    b, n, g = build_raw_stage(
        duration=120,
        carrier=220,
        start_beat=10.0,
        end_beat=9.1,
        binaural_start=0.035,
        binaural_end=0.095,
        noise_start=0.001,
        noise_end=0.006,
        guide_volume=0.0025,
        guide_pulse_start=0.035,
        guide_pulse_end=0.030,
    )
    binaural_stages.append(b)
    noise_stages.append(n)
    guide_stages.append(g)

    # 2:00–5:00 — глубина через бинаурал, не через шум
    b, n, g = build_raw_stage(
        duration=180,
        carrier=220,
        start_beat=9.1,
        end_beat=7.2,
        binaural_start=0.095,
        binaural_end=0.215,
        noise_start=0.006,
        noise_end=0.014,
        guide_volume=0.0045,
        guide_pulse_start=0.030,
        guide_pulse_end=0.025,
    )
    binaural_stages.append(b)
    noise_stages.append(n)
    guide_stages.append(g)

    # 5:00–9:00 — глубокое плато: почти неподвижное состояние
    b, n, g = build_raw_stage(
        duration=240,
        carrier=220,
        start_beat=7.2,
        end_beat=6.9,
        binaural_start=0.215,
        binaural_end=0.205,
        noise_start=0.014,
        noise_end=0.014,
        guide_volume=0.0025,
        guide_pulse_start=0.025,
        guide_pulse_end=0.023,
    )
    binaural_stages.append(b)
    noise_stages.append(n)
    guide_stages.append(g)

    # 9:00–11:00 — удержание тишины, мягкое снижение плотности
    b, n, g = build_raw_stage(
        duration=120,
        carrier=220,
        start_beat=6.9,
        end_beat=6.6,
        binaural_start=0.205,
        binaural_end=0.150,
        noise_start=0.014,
        noise_end=0.009,
        guide_volume=0.002,
        guide_pulse_start=0.023,
        guide_pulse_end=0.022,
    )
    binaural_stages.append(b)
    noise_stages.append(n)
    guide_stages.append(g)

    # 11:00–12:00 — выход без рывка
    b, n, g = build_raw_stage(
        duration=60,
        carrier=220,
        start_beat=6.6,
        end_beat=8.0,
        binaural_start=0.110,
        binaural_end=0.050,
        noise_start=0.007,
        noise_end=0.001,
        guide_volume=0.001,
        guide_pulse_start=0.022,
        guide_pulse_end=0.030,
    )
    binaural_stages.append(b)
    noise_stages.append(n)
    guide_stages.append(g)

    full_binaural = concatenate_stages(binaural_stages)
    full_noise = concatenate_stages(noise_stages)
    full_guide = concatenate_stages(guide_stages)

    audio = mix_layers([full_binaural, full_noise, full_guide])

    output_path = OUTPUT_AUDIO / "NeoSphere_Reset_01_v3_12min.wav"
    save_wav(audio, output_path)


if __name__ == "__main__":
    generate_reset_01_v3()
