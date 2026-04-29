import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from app.config import LIB_PATH
sys.path.append(str(LIB_PATH))

from core.video_engine import create_video


OUTPUT_VIDEO = ROOT / "output" / "video"


def generate_video():
    duration = 12 * 60
    output_path = OUTPUT_VIDEO / "NeoSphere_Reset_01_visual.mp4"
    create_video(duration, str(output_path))


if __name__ == "__main__":
    generate_video()
