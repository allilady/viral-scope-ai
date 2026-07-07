import base64
import json
import os
import sys
from pathlib import Path

from frames import frame_time, pick_keyframes


PROJECT_DIR = Path(__file__).resolve().parent

SYSTEM_PROMPT = """You are a cross-border e-commerce creator-marketing content strategist.
Your job is to break down why a short video gets traffic, and whether it has conversion potential.

Base your analysis on:
1. The video screenshot timeline
2. The video's basic info provided by the operator
3. The creator profile
4. The performance metrics
5. The voiceover / caption summary

Output a structured analysis.

Rules:
- Write the ENTIRE report in English, including all section headings. Use the exact headings given in the user prompt — do not rename or renumber them.
- Be plain and direct, no empty theory.
- Every conclusion must map to an executable action.
- You MUST separate "traffic reasons" from "conversion reasons".
- You MUST give feedback a creator can directly understand and act on.
- If information is insufficient, say exactly what is missing instead of making things up.
"""


def load_config():
    config_path = PROJECT_DIR / "config.json"
    if not config_path.exists():
        print("缺少 config.json，请先复制模板: cp config.example.json config.json")
        sys.exit(1)

    with config_path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    config.setdefault("openai_base_url", "https://api.openai.com/v1")
    config.setdefault("openai_model", "gpt-5.4")

    return config


def build_user_prompt(video_name, data, keyframes):
    frame_lines = [
        f"- {frame_time(frame):.1f}s: {frame.as_posix()}" for frame in keyframes
    ]

    return f"""Generate a complete Markdown analysis report based on the video info and keyframes below.

You MUST use the exact Markdown structure below (headings in English, verbatim — do NOT rename or renumber them):

# ViralScope AI Video Breakdown

## 1. Basic Info
## 2. Why It Went Viral
## 3. First 3-Second Hook
## 4. Content Structure
## 5. Emotional Value
## 6. Repeatable Viral Formula
## 7. Remake & Optimization
### Copy Directly (3)
### Do Better (2)
### Our Brand Version
## 8. Conversion Diagnosis
## 9. Creator Feedback

Acceptance criteria:
- Every viral reason must cite a specific timestamp or on-screen detail.
- Every remake suggestion must be a one-line instruction the creator can execute directly.
- You must separate traffic reasons from conversion reasons.
- Output at least 3 copyable points, 2 improvement points, and 1 brand-account landing version.
- If information is insufficient, state exactly what is missing — do not fabricate.
- Under "## 6. Repeatable Viral Formula", give a reusable template structure.
- Under "### Our Brand Version", write a ready-to-shoot English script / shot list the brand account can film directly.

Video name: {video_name}

JSON basic info:
```json
{json.dumps(data, ensure_ascii=False, indent=2)}
```

Keyframes for this run:
{chr(10).join(frame_lines)}
"""


def save_report(video_name, text):
    output_dir = PROJECT_DIR / "outputs" / video_name
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "report_openai.md"
    report_path.write_text(text, encoding="utf-8")
    print(f"AI分析报告已生成: {report_path}")
    return report_path


def image_data_uri(frame_path):
    encoded = base64.b64encode(frame_path.read_bytes()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


def call_openai_chat(config, messages, timeout=300):
    if not os.environ.get("OPENAI_API_KEY"):
        print("OpenAI 调用失败: 缺少环境变量 OPENAI_API_KEY")
        sys.exit(1)

    try:
        import requests
    except ImportError as error:
        print(f"OpenAI 调用失败: 依赖未安装: {error}")
        print("请先运行: pip install requests")
        sys.exit(1)

    try:
        endpoint = config["openai_base_url"].rstrip("/") + "/chat/completions"
        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json",
            },
            json={
                "model": config["openai_model"],
                "messages": messages,
            },
            timeout=timeout,
        )
        if response.status_code >= 400:
            print(f"OpenAI 调用失败: HTTP {response.status_code}: {response.text[:500]}")
            sys.exit(1)

        result = response.json()
        text = result["choices"][0]["message"]["content"]
        if not text:
            print("OpenAI 调用失败: 返回结果为空")
            sys.exit(1)
        return text
    except Exception as error:
        print(f"OpenAI 调用失败: {type(error).__name__}: {error}")
        sys.exit(1)


def analyze_with_openai(config, prompt, keyframes):
    content = [{"type": "text", "text": prompt}]
    for frame in keyframes:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": image_data_uri(frame)},
            }
        )

    return call_openai_chat(
        config,
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
    )


def analyze_video(video_name):
    config = load_config()
    json_path = PROJECT_DIR / "samples" / f"{video_name}.json"
    frames_dir = PROJECT_DIR / "outputs" / video_name / "frames"

    with json_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    try:
        keyframes = pick_keyframes(frames_dir)
    except FileNotFoundError as error:
        print(f"分析失败: {error}")
        sys.exit(1)

    prompt = build_user_prompt(video_name, data, keyframes)

    print(
        "AI分析使用 OpenAI-compatible API:",
        config["openai_base_url"],
        "关键帧:",
        ", ".join(f"{frame_time(frame):.1f}s" for frame in keyframes),
    )

    report = analyze_with_openai(config, prompt, keyframes)
    return save_report(video_name, report)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python analyze_video.py <video_name>")
        sys.exit(1)

    analyze_video(sys.argv[1])
