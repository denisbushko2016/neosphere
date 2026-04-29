from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip


ROOT = Path(__file__).resolve().parents[2]

AUDIO_PATH = ROOT / "output" / "audio" / "NeoSphere_Reset_01_BASE.wav"
VIDEO_PATH = ROOT / "output" / "video" / "NeoSphere_Reset_01_visual.mp4"
OUTPUT_PATH = ROOT / "output" / "video" / "NeoSphere_Reset_01_FULL.mp4"


def build_full_session():
    video = VideoFileClip(str(VIDEO_PATH))
    audio = AudioFileClip(str(AUDIO_PATH))

    video = video.set_audio(audio)

    video.write_videofile(
        str(OUTPUT_PATH),
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    video.close()
    audio.close()


if __name__ == "__main__":
    build_full_session()
