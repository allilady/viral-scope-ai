import json
import sys
from pathlib import Path

from frames import frame_time


def build_report(video_name):
    json_path = Path("samples") / f"{video_name}.json"
    frames_dir = Path("outputs") / video_name / "frames"
    report_path = Path("outputs") / video_name / "ViralScope_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with json_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    creator = data.get("creator_profile", {})
    metrics = data.get("metrics", {})
    frames = sorted(frames_dir.glob("frame_*.jpg"), key=frame_time)

    lines = [
        "# ViralScope AI 热点视频拆解报告",
        "",
        "## 一、基础信息",
        "",
        f"- 视频文件: {data.get('video', '')}",
        f"- 平台: {data.get('platform', '')}",
        f"- 类目: {data.get('category', '')}",
        f"- 产品类型: {data.get('product_type', '')}",
        f"- 目标人群: {data.get('target_audience', '')}",
        f"- 投放类型: {data.get('campaign_type', '')}",
        f"- 标题: {data.get('title', '')}",
        f"- 口播摘要: {data.get('speech_summary', '')}",
        "",
        "### 达人画像",
        "",
        f"- 国家: {creator.get('country', '')}",
        f"- 语言: {creator.get('language', '')}",
        f"- 垂类: {creator.get('niche', '')}",
        f"- 粉丝层级: {creator.get('follower_tier', '')}",
        f"- 风格: {creator.get('style', '')}",
        f"- 人群匹配度: {creator.get('audience_fit', '')}",
        "",
        "### 数据表现",
        "",
        f"- 播放量: {metrics.get('views', '')}",
        f"- 点赞: {metrics.get('likes', '')}",
        f"- 评论: {metrics.get('comments', '')}",
        f"- 收藏: {metrics.get('saves', '')}",
        f"- 分享: {metrics.get('shares', '')}",
        f"- 完播率: {metrics.get('completion_rate', '')}",
        f"- 订单数: {metrics.get('orders', '')}",
        f"- GMV: {metrics.get('gmv', '')}",
        f"- 样品成本: {metrics.get('sample_cost', '')}",
        f"- 运营备注: {data.get('operator_note', '')}",
        "",
        "## 截图时间轴",
        "",
        "| 时间点 | 截图文件相对路径 | 备注 |",
        "| --- | --- | --- |",
    ]

    for frame in frames:
        seconds = frame_time(frame)
        relative_path = frame.as_posix()
        lines.append(f"| {seconds:.1f}s | {relative_path} |  |")

    lines.extend(
        [
            "",
            "## 二、爆款核心原因",
            "",
            "## 三、Hook拆解",
            "",
            "## 四、内容结构拆解",
            "",
            "## 五、产品卖点与用户痛点",
            "",
            "## 六、评论区与转化线索",
            "",
            "## 七、可复用脚本模板",
            "",
            "## 八、优化建议",
            "",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"报告已生成: {report_path}")
    return report_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python build_timeline.py <video_name>")
        sys.exit(1)

    build_report(sys.argv[1])
