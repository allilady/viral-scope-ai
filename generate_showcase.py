import html
import json
import re
import sys
from pathlib import Path

from frames import frame_time, pick_keyframes


PROJECT_DIR = Path(__file__).resolve().parent


def read_json(video_name):
    json_path = PROJECT_DIR / "samples" / f"{video_name}.json"
    if not json_path.exists():
        print(f"生成失败: 找不到视频数据文件: {json_path}")
        sys.exit(1)

    with json_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def require_report_files(video_name):
    output_dir = PROJECT_DIR / "outputs" / video_name
    report_path = output_dir / "report_openai.md"
    diagnosis_path = output_dir / "diagnosis.md"

    missing = [path for path in [report_path, diagnosis_path] if not path.exists()]
    if missing:
        print("请先运行main.py和diagnose.py生成对应的分析报告")
        for path in missing:
            print(f"缺少文件: {path}")
        sys.exit(1)

    return report_path, diagnosis_path


def load_keyframes(video_name):
    frames_dir = PROJECT_DIR / "outputs" / video_name / "frames"
    try:
        return pick_keyframes(frames_dir)
    except FileNotFoundError as error:
        print(f"生成失败: {error}")
        sys.exit(1)


def fmt_metric(value):
    if value == "" or value is None:
        return "-"
    if isinstance(value, int) and value >= 1000:
        if value >= 1000000:
            return f"{value / 1000000:.1f}M".replace(".0M", "M")
        if value >= 10000:
            return f"{value / 1000:.0f}K"
        return f"{value:,}"
    return str(value)


def strip_markdown(text):
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"^\s*[-*>#]+\s*", "", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Markdown 解析：从报告里按标题抽取版块，并把版块渲染成 HTML
# ---------------------------------------------------------------------------

def extract_section(report_text, keywords):
    """抽取标题含任一 keyword 的 markdown 版块正文（到下一个同级或更高级标题为止）。

    keywords 可传单个字符串或列表；列表用于同时兼容英文/中文标题。
    """
    if isinstance(keywords, str):
        keywords = [keywords]

    lines = report_text.splitlines()
    start = None
    start_level = 0

    for index, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("#") and any(k in line for k in keywords):
            start = index + 1
            start_level = len(stripped) - len(stripped.lstrip("#"))
            break

    if start is None:
        return ""

    body = []
    for line in lines[start:]:
        stripped = line.lstrip()
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            if level <= start_level:
                break
        body.append(line)

    return "\n".join(body).strip()


def inline_md(text):
    """行内 markdown -> HTML（先转义再套标签，顺序不能反）。"""
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    return escaped


def markdown_block_to_html(md):
    """把一个 markdown 版块渲染成 HTML，保留标题/有序/无序列表/段落结构。"""
    if not md:
        return '<p class="empty">No content yet — please re-run the analysis.</p>'

    html_parts = []
    list_items = []
    list_tag = None

    def flush_list():
        nonlocal list_items, list_tag
        if list_items:
            html_parts.append(
                f"<{list_tag}>" + "".join(f"<li>{item}</li>" for item in list_items) + f"</{list_tag}>"
            )
            list_items = []
            list_tag = None

    for raw in md.splitlines():
        line = raw.strip()
        if not line:
            flush_list()
            continue

        heading = re.match(r"^#{1,6}\s+(.*)$", line)
        ordered = re.match(r"^\d+[.、]\s+(.*)$", line)
        unordered = re.match(r"^[-*]\s+(.*)$", line)

        if heading:
            flush_list()
            html_parts.append(f"<h4>{inline_md(heading.group(1))}</h4>")
        elif ordered:
            if list_tag not in (None, "ol"):
                flush_list()
            list_tag = "ol"
            list_items.append(inline_md(ordered.group(1)))
        elif unordered:
            if list_tag not in (None, "ul"):
                flush_list()
            list_tag = "ul"
            list_items.append(inline_md(unordered.group(1)))
        else:
            flush_list()
            html_parts.append(f"<p>{inline_md(line)}</p>")

    flush_list()
    return "\n".join(html_parts)


SECTION_MODES = {1: "type", 2: "conclusion", 3: "actions", 4: "feedback"}


def diagnosis_section_index(line):
    """识别诊断版块边界：中文 `一、二、三、四、` 或英文 markdown 标题 `## 1.`。

    注意：英文版块必须带 `#` 前缀，避免把正文里的有序列表项 `1.` 误判成版块。
    """
    cjk = re.match(r"^([一二三四])、", line)
    if cjk:
        return "一二三四".index(cjk.group(1)) + 1

    en = re.match(r"^#{1,6}\s*([1-4])[.)]", line)
    if en:
        return int(en.group(1))

    return None


def diagnosis_sections(diagnosis_text):
    """从 diagnosis.md 抽一句话结论、三条优先动作、达人反馈话术（兼容中/英标题）。"""
    lines = [line.rstrip() for line in diagnosis_text.splitlines()]
    conclusion = ""
    actions = []
    feedback = []
    mode = None
    current_action = []

    def flush_action():
        nonlocal current_action
        if current_action:
            actions.append(" ".join(current_action))
            current_action = []

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        index = diagnosis_section_index(line)
        if index is not None:
            flush_action()
            mode = SECTION_MODES[index]
            continue

        if mode == "conclusion" and not conclusion:
            conclusion = strip_markdown(line)
        elif mode == "actions":
            if re.match(r"^\d+[.、]", line) or line.startswith("### "):
                flush_action()
                current_action = [re.sub(r"^\d+[.、]\s*", "", strip_markdown(line))]
            elif current_action:
                current_action.append(strip_markdown(line))
        elif mode == "feedback":
            feedback.append(strip_markdown(line))

    flush_action()

    return {
        "conclusion": conclusion or "No one-line diagnosis yet.",
        "actions": actions[:3] or ["No action suggestions yet."],
        "feedback": feedback or ["No creator feedback yet."],
    }


def page_subtitle(data):
    platform = data.get("platform", "Unknown platform")
    category = data.get("category", "unknown category")
    audience = data.get("target_audience", "target audience")
    product = data.get("product_type", "product")
    return (
        f"{platform} / {category} / {product} breakdown — "
        f"for {audience}: what's worth copying first, then where conversion stalls."
    )


def filmstrip_html(keyframes):
    shots = []
    for frame in keyframes:
        seconds = frame_time(frame)
        rel_path = f"frames/{frame.name}"
        shots.append(
            f"""        <figure class="frame">
          <img src="{html.escape(rel_path)}" alt="Frame at {seconds:.1f}s">
          <figcaption>{seconds:.1f}s</figcaption>
        </figure>"""
        )
    return "\n".join(shots)


def render_html(video_name, data, report_text, diagnosis_text, keyframes):
    metrics = data.get("metrics", {})
    diagnosis = diagnosis_sections(diagnosis_text)

    formula_html = markdown_block_to_html(
        extract_section(report_text, ["Repeatable Viral Formula", "可复制爆款公式"])
    )
    landing_html = markdown_block_to_html(
        extract_section(report_text, ["Our Brand Version", "适合我们账号的落地版本"])
    )

    actions_html = "\n".join(
        f"            <li>{html.escape(action)}</li>" for action in diagnosis["actions"]
    )
    feedback_html = "\n".join(
        f"        <p>{html.escape(part)}</p>" for part in diagnosis["feedback"]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ViralScope AI | {html.escape(video_name)}</title>
  <style>
    :root {{
      --bg: #151515;
      --text: #f2efe9;
      --muted: #aaa39b;
      --line: #3b3937;
      --accent: #ff6a3d;
      --accent-2: #e650b6;
      --good: #4fd18b;
      --good-soft: rgba(79, 209, 139, 0.12);
      --warn: #ff9d54;
      --warn-soft: rgba(255, 106, 61, 0.12);
      --gold: #ffd18c;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background:
        radial-gradient(circle at 16% 0%, rgba(230, 80, 182, 0.16), transparent 32rem),
        radial-gradient(circle at 85% 12%, rgba(255, 106, 61, 0.12), transparent 28rem),
        var(--bg);
      color: var(--text);
      font-family: "Segoe UI", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif;
      line-height: 1.65;
    }}

    .page {{
      width: min(1100px, calc(100% - 48px));
      margin: 0 auto;
      padding: 56px 0 80px;
    }}

    .hero {{
      border-bottom: 1px solid rgba(255, 106, 61, 0.42);
      padding-bottom: 34px;
      margin-bottom: 44px;
    }}

    .eyebrow {{
      margin: 0 0 10px;
      color: var(--accent);
      font-family: Consolas, "Cascadia Mono", monospace;
      font-size: 13px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    h1 {{
      margin: 0;
      font-size: clamp(40px, 6vw, 72px);
      line-height: 0.95;
      font-weight: 900;
    }}

    .subtitle {{
      max-width: 820px;
      margin: 18px 0 0;
      color: var(--muted);
      font-size: 18px;
    }}

    .metrics {{
      display: grid;
      grid-template-columns: repeat(6, minmax(100px, 1fr));
      gap: 1px;
      margin-top: 32px;
      background: var(--line);
      border: 1px solid var(--line);
    }}

    .metric {{ background: rgba(26, 26, 26, 0.92); padding: 18px; }}

    .metric strong {{
      display: block;
      color: var(--gold);
      font-family: Consolas, "Cascadia Mono", monospace;
      font-size: 25px;
      line-height: 1.1;
    }}

    .metric span {{ display: block; margin-top: 6px; color: var(--muted); font-size: 13px; }}

    .section-title {{
      display: flex;
      align-items: center;
      gap: 14px;
      margin: 0 0 22px;
      font-size: 24px;
      font-weight: 850;
    }}

    .section-title::after {{
      content: "";
      height: 1px;
      flex: 1;
      background: linear-gradient(90deg, currentColor, transparent);
      opacity: 0.5;
    }}

    /* keyframe filmstrip */
    .filmstrip {{
      display: flex;
      gap: 12px;
      overflow-x: auto;
      padding-bottom: 12px;
      margin-bottom: 60px;
    }}

    .frame {{ flex: 0 0 auto; margin: 0; width: 96px; }}

    .frame img {{
      display: block;
      width: 96px;
      aspect-ratio: 9 / 16;
      object-fit: cover;
      background: #0f0f0f;
      border: 1px solid rgba(255, 255, 255, 0.12);
    }}

    .frame figcaption {{
      margin-top: 6px;
      text-align: center;
      color: var(--accent);
      font-family: Consolas, "Cascadia Mono", monospace;
      font-size: 12px;
    }}

    /* good / warn blocks */
    .block {{ margin-bottom: 62px; }}
    .block.good {{ color: var(--good); }}
    .block.warn {{ color: var(--warn); }}

    .cards {{ display: grid; grid-template-columns: 1fr 1fr; gap: 26px; }}

    .card {{
      color: var(--text);
      padding: 24px 26px;
      border-radius: 4px;
    }}

    .good .card {{
      background: var(--good-soft);
      border-left: 3px solid var(--good);
    }}

    .warn .card {{
      background: var(--warn-soft);
      border-left: 3px solid var(--warn);
    }}

    .card > h3 {{
      margin: 0 0 14px;
      font-size: 18px;
    }}

    .good .card > h3 {{ color: var(--good); }}
    .warn .card > h3 {{ color: var(--warn); }}

    .card p {{ margin: 0 0 12px; color: var(--text); font-size: 15px; }}
    .card p.empty {{ color: var(--muted); }}
    .card h4 {{ margin: 16px 0 8px; font-size: 15px; color: var(--gold); }}
    .card ul, .card ol {{ margin: 0 0 12px; padding-left: 20px; }}
    .card li {{ margin-bottom: 8px; color: var(--text); font-size: 15px; }}
    .card code {{
      font-family: Consolas, "Cascadia Mono", monospace;
      font-size: 14px;
      background: rgba(255, 255, 255, 0.08);
      padding: 1px 5px;
    }}

    .conclusion {{
      font-size: 17px;
      color: var(--text);
      border-left: 3px solid var(--warn);
      background: var(--warn-soft);
      padding: 18px 22px;
      margin-bottom: 20px;
    }}

    @media (max-width: 900px) {{
      .metrics {{ grid-template-columns: repeat(3, 1fr); }}
      .cards {{ grid-template-columns: 1fr; }}
    }}

    @media (max-width: 560px) {{
      .metrics {{ grid-template-columns: repeat(2, 1fr); }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <header class="hero">
      <p class="eyebrow">ViralScope AI / {html.escape(video_name)}</p>
      <h1>ViralScope AI</h1>
      <p class="subtitle">{html.escape(page_subtitle(data))}</p>
      <div class="metrics" aria-label="Key metrics">
        <div class="metric"><strong>{html.escape(fmt_metric(metrics.get("views")))}</strong><span>Views</span></div>
        <div class="metric"><strong>{html.escape(fmt_metric(metrics.get("likes")))}</strong><span>Likes</span></div>
        <div class="metric"><strong>{html.escape(fmt_metric(metrics.get("comments")))}</strong><span>Comments</span></div>
        <div class="metric"><strong>{html.escape(fmt_metric(metrics.get("saves")))}</strong><span>Saves</span></div>
        <div class="metric"><strong>{html.escape(fmt_metric(metrics.get("shares")))}</strong><span>Shares</span></div>
        <div class="metric"><strong>{html.escape(fmt_metric(metrics.get("orders")))}</strong><span>Orders</span></div>
      </div>
    </header>

    <section aria-labelledby="frames-title">
      <h2 class="section-title" id="frames-title" style="color: var(--accent-2);">Key Frames</h2>
      <div class="filmstrip">
{filmstrip_html(keyframes)}
      </div>
    </section>

    <section class="block good" aria-labelledby="good-title">
      <h2 class="section-title" id="good-title">✅ What's Working — Repeatable</h2>
      <div class="cards">
        <div class="card">
          <h3>Repeatable Viral Formula</h3>
          {formula_html}
        </div>
        <div class="card">
          <h3>Our Brand Version</h3>
          {landing_html}
        </div>
      </div>
    </section>

    <section class="block warn" aria-labelledby="warn-title">
      <h2 class="section-title" id="warn-title">⚠️ What to Fix</h2>
      <div class="conclusion">{html.escape(diagnosis["conclusion"])}</div>
      <div class="cards">
        <div class="card">
          <h3>Conversion Diagnosis · Priority Actions</h3>
          <ol>
{actions_html}
          </ol>
        </div>
        <div class="card">
          <h3>Creator Feedback</h3>
{feedback_html}
        </div>
      </div>
    </section>
  </main>
</body>
</html>
"""


def generate_showcase(video_name):
    data = read_json(video_name)
    report_path, diagnosis_path = require_report_files(video_name)
    keyframes = load_keyframes(video_name)

    report_text = report_path.read_text(encoding="utf-8")
    diagnosis_text = diagnosis_path.read_text(encoding="utf-8")
    output_path = PROJECT_DIR / "outputs" / video_name / "showcase.html"
    output_path.write_text(
        render_html(video_name, data, report_text, diagnosis_text, keyframes),
        encoding="utf-8",
    )
    print(f"展示页已生成: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python generate_showcase.py <video_name>")
        sys.exit(1)

    generate_showcase(sys.argv[1])
