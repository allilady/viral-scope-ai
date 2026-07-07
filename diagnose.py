import json
import sys
from pathlib import Path

from analyze_video import call_openai_chat, load_config


PROJECT_DIR = Path(__file__).resolve().parent

DIAGNOSIS_PROMPT = """You are a creator-marketing content review consultant. You will receive a finished viral-video breakdown report, the video's real performance metrics, and the system's performance classification based on views and orders.

Your job is NOT to repeat the analysis already in the report, but to produce a review matching the classification result:

A. High views, high conversion: strong performance — focus on extracting repeatable wins, not fault-finding.
B. High views, low conversion: diagnose the conversion blockers, output priority fixes.
C. Low views but decent conversion: explain why it's niche-but-precise, extract audience-fit and conversion-efficiency reasons.
D. Both low: diagnose fundamental issues — creator fit, content quality, product framing, trust.

Write the ENTIRE review in English. Use exactly these four Markdown headings, verbatim, in this order — do not rename or renumber them:

## 1. Type Judgment
(state A/B/C/D clearly plus the reasoning)

## 2. One-Sentence Conclusion
(a single-sentence review takeaway)

## 3. Top Priority Actions
(the three most important review conclusions or actions)
   - Type A: write repeatable wins, not a problem list
   - Type B: write the highest-priority concrete fixes
   - Type C: write the niche-precision reasons and how to scale it
   - Type D: write the fundamental issues and whether to keep working with the creator

## 4. Creator Feedback
(a message ready to copy-paste and send, friendly tone, affirm strengths first then give suggestions)"""


def report_path(video_name):
    path = PROJECT_DIR / "outputs" / video_name / "report_openai.md"
    if path.exists():
        return path

    print(f"诊断失败: 找不到AI分析报告文件: {path}")
    sys.exit(1)


def load_metrics(video_name):
    json_path = PROJECT_DIR / "samples" / f"{video_name}.json"
    if not json_path.exists():
        print(f"诊断失败: 找不到视频数据文件: {json_path}")
        sys.exit(1)

    with json_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    metrics = data.get("metrics", {})
    return {
        "views": metrics.get("views", ""),
        "likes": metrics.get("likes", ""),
        "comments": metrics.get("comments", ""),
        "saves": metrics.get("saves", ""),
        "shares": metrics.get("shares", ""),
        "orders": metrics.get("orders", ""),
    }


def as_number(value):
    if value == "" or value is None:
        return 0
    try:
        return float(str(value).replace(",", "").strip())
    except ValueError:
        return 0


def classify_case(metrics):
    views = as_number(metrics.get("views"))
    orders = as_number(metrics.get("orders"))

    high_play = views >= 100000
    good_conversion = orders >= 50

    if high_play and good_conversion:
        return {
            "type": "A",
            "label": "高播放高转化",
            "reason": f"播放量 {views:.0f} >= 100000, 订单 {orders:.0f} >= 50",
        }
    if high_play and not good_conversion:
        return {
            "type": "B",
            "label": "高播放低转化",
            "reason": f"播放量 {views:.0f} >= 100000, 订单 {orders:.0f} < 50",
        }
    if not high_play and good_conversion:
        return {
            "type": "C",
            "label": "低播放但转化尚可",
            "reason": f"播放量 {views:.0f} < 100000, 订单 {orders:.0f} >= 50",
        }
    return {
        "type": "D",
        "label": "双低",
        "reason": f"播放量 {views:.0f} < 100000, 订单 {orders:.0f} < 50",
    }


def build_context(report_text, metrics, case_type):
    return f"""请基于以下上下文生成复盘分析。

系统分类:
```json
{json.dumps(case_type, ensure_ascii=False, indent=2)}
```

真实数据表现:
```json
{json.dumps(metrics, ensure_ascii=False, indent=2)}
```

已完成的爆款视频拆解报告:
```markdown
{report_text}
```
"""


def diagnose(video_name):
    path = report_path(video_name)
    report_text = path.read_text(encoding="utf-8")
    metrics = load_metrics(video_name)
    case_type = classify_case(metrics)
    config = load_config()

    print("转化诊断使用报告:", path)
    print("视频表现分类:", f"{case_type['type']}. {case_type['label']}", case_type["reason"])
    print("转化诊断使用 OpenAI-compatible API:", config["openai_base_url"])

    diagnosis = call_openai_chat(
        config,
        [
            {"role": "system", "content": DIAGNOSIS_PROMPT},
            {"role": "user", "content": build_context(report_text, metrics, case_type)},
        ],
        timeout=120,
    )

    output_path = PROJECT_DIR / "outputs" / video_name / "diagnosis.md"
    output_path.write_text(diagnosis, encoding="utf-8")
    print(f"转化诊断报告已生成: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python diagnose.py <video_name>")
        sys.exit(1)

    diagnose(sys.argv[1])
