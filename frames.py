"""帧工具模块：抽帧命名解析、列举与关键帧选择的唯一实现。

其它脚本统一从这里 import，避免 frame_time / pick_keyframes 各写一份。
"""

import re
from pathlib import Path


# 关键帧目标时间点：前 3 秒密集（决定停留），中后段稀疏（看结构和转化）。
# pick_keyframes 会为每个目标点选最接近的已抽帧，天然把输入控制在 <=14 张，
# 既可解释又不会让多模态请求超时。
TARGET_TIMES = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 5.0, 8.0, 12.0, 18.0, 30.0, 45.0, 60.0]


def frame_time(frame_path):
    """从 frame_<秒>s.jpg 文件名解析时间点，兼容任意小数位。"""
    match = re.search(r"frame_([\d.]+)s\.jpg$", Path(frame_path).name)
    if not match:
        return 0.0
    return float(match.group(1))


def list_frames(frames_dir):
    """返回按时间排序的帧列表；目录为空时抛 FileNotFoundError。"""
    frames_dir = Path(frames_dir)
    frames = sorted(frames_dir.glob("frame_*.jpg"), key=frame_time)
    if not frames:
        raise FileNotFoundError(f"找不到截图文件: {frames_dir}")
    return frames


def pick_keyframes(frames_dir):
    """按 TARGET_TIMES 为每个目标点选最接近的已抽帧，去重后按时间返回。"""
    frames = list_frames(frames_dir)

    picked = {}
    for target in TARGET_TIMES:
        # 超出视频长度的目标点直接跳过，避免重复选到最后一帧。
        if target > frame_time(frames[-1]) + 0.001:
            continue
        nearest = min(frames, key=lambda frame: abs(frame_time(frame) - target))
        picked[nearest] = frame_time(nearest)

    return sorted(picked, key=lambda frame: picked[frame])
