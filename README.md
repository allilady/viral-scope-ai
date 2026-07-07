# ViralScope AI

面向跨境电商 / 出海达人运营的本地 AI 复盘工作流：人工挑出值得拆解的热点视频后，脚本自动抽帧、用 AI 生成结构化「爆款拆解报告」和「转化诊断」，最后汇成一页可分享的展示页。

AI 分析产出（爆款拆解报告、转化诊断、展示页）统一为英文，可直接发给海外达人；本仓库的说明文档用中文，方便运营阅读。

## 流程

```
samples/<name>.mp4 + <name>.json
        │
        ▼
  main.py ── 抽帧 ─▶ 时间轴报告 ─▶ AI 爆款拆解 (report_openai.md)
        │
        ▼
  diagnose.py ─▶ 转化诊断 (diagnosis.md)
        │
        ▼
  generate_showcase.py ─▶ 展示页 (showcase.html)
```

## 环境准备

```bash
pip install -r requirements.txt        # 依赖：requests
cp config.example.json config.json     # 按需改成你的 OpenAI-compatible 中转地址
export OPENAI_API_KEY=sk-...            # Windows PowerShell: $env:OPENAI_API_KEY="sk-..."
```

系统需要 `ffmpeg` / `ffprobe`（优先用 PATH 里的；Windows 下也可回退到 `ffmpeg-bin/` 本地构建）。

## 运行

```bash
python main.py <video_name>                # 抽帧 + 时间轴 + AI 拆解
python diagnose.py <video_name>            # 转化诊断
python generate_showcase.py <video_name>   # 生成展示页
```

`<video_name>` 对应 `samples/<video_name>.mp4` 和 `samples/<video_name>.json`。

## 输出文件

| 文件 | 说明 |
|---|---|
| `outputs/<name>/frames/` | 三段式抽帧截图 |
| `outputs/<name>/ViralScope_report.md` | 本地基础时间轴报告（不依赖 AI） |
| `outputs/<name>/report_openai.md` | AI 爆款拆解报告 |
| `outputs/<name>/diagnosis.md` | 转化诊断报告 |
| `outputs/<name>/showcase.html` | 汇总展示页 |

`outputs/` 为生成产物，不纳入版本控制。

## GitHub Pages 发布

仓库已准备 `docs/` 作为 GitHub Pages 静态站点目录：

| 路径 | 说明 |
|---|---|
| `docs/index.html` | Demo 入口页，链接到 video1 / video2 |
| `docs/video1/showcase.html` | video1 展示页副本 |
| `docs/video1/frames/` | video1 展示页引用的关键帧 |
| `docs/video2/showcase.html` | video2 展示页副本 |
| `docs/video2/frames/` | video2 展示页引用的关键帧 |

首次推送到 GitHub：

```bash
git remote remove origin
git remote add origin https://github.com/<your-user>/viral-scope-ai.git
git push -u origin master
```

如果希望使用 `main` 分支：

```bash
git branch -M main
git push -u origin main
```

GitHub Pages 设置：

1. 打开仓库 `Settings -> Pages`。
2. `Source` 选择 `Deploy from a branch`。
3. `Branch` 选择 `master` 或 `main`，目录选择 `/docs`。
4. 保存后访问 `https://<your-user>.github.io/viral-scope-ai/`。

更新在线展示页时，先重跑脚本，再把 `outputs/<name>/showcase.html` 和页面引用的 `frames/*.jpg` 同步到 `docs/<name>/`，随后提交并推送。
