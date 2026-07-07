import sys
from pathlib import Path

from build_timeline import build_report
from extract_frames import extract_frames
from analyze_video import analyze_video


def main(video_name):
    video_path = Path("samples") / f"{video_name}.mp4"
    json_path = Path("samples") / f"{video_name}.json"

    if not video_path.exists():
        print(f"找不到视频文件: {video_path}")
        sys.exit(1)

    if not json_path.exists():
        print(f"找不到JSON文件: {json_path}")
        sys.exit(1)

    extract_frames(video_path)
    build_report(video_name)
    analyze_video(video_name)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python main.py <video_name>")
        sys.exit(1)

    main(sys.argv[1])
