import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
LOCAL_FFMPEG_DIR = PROJECT_DIR / "ffmpeg-bin" / "ffmpeg-8.1.2-essentials_build" / "bin"


def tool_path(name):
    """优先用系统 PATH 里的 ffmpeg/ffprobe（跨平台），仅在找不到时回退到本地 Windows 构建。"""
    found = shutil.which(name)
    if found:
        return found

    local = LOCAL_FFMPEG_DIR / f"{name}.exe"
    if local.exists():
        return str(local)

    return name


def build_time_points(video_path):
    duration_cmd = [
        tool_path("ffprobe"),
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    duration = float(subprocess.check_output(duration_cmd, text=True).strip())

    points = []
    current = 0.0
    while current <= min(duration, 3.0) + 0.001:
        points.append(round(current, 1))
        current += 0.5

    current = 4.0
    while current <= min(duration, 15.0) + 0.001:
        points.append(round(current, 1))
        current += 1.0

    current = 17.0
    while current <= duration + 0.001:
        points.append(round(current, 1))
        current += 2.0

    return points


def extract_frames(video_path):
    video_path = Path(video_path)
    video_name = video_path.stem
    output_dir = Path("outputs") / video_name / "frames"
    output_dir.mkdir(parents=True, exist_ok=True)

    time_points = build_time_points(video_path)

    for point in time_points:
        output_file = output_dir / f"frame_{point:.1f}s.jpg"
        cmd = [
            tool_path("ffmpeg"),
            "-y",
            "-i",
            str(video_path),
            "-ss",
            f"{point:.1f}",
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(output_file),
        ]
        subprocess.run(cmd, check=True)

    print(f"一共生成了 {len(time_points)} 张截图")
    print("时间点列表:", ", ".join(f"{point:.1f}s" for point in time_points))
    return time_points


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python extract_frames.py samples/<video_name>.mp4")
        sys.exit(1)

    extract_frames(sys.argv[1])
