# ViralScope AI Progress

更新时间: 2026-07-06

## 当前状态

工具 1 的本地核心闭环已经跑通:

- `main.py` 可以按视频名执行完整流程: 抽帧 -> 读取 JSON -> 生成 Markdown 报告。
- `extract_frames.py` 已改为三段式抽帧:
  - 0-3 秒: 每 0.5 秒 1 帧
  - 3-15 秒: 每 1 秒 1 帧
  - 15 秒后: 每 2 秒 1 帧
- `build_timeline.py` 可以生成基础信息和截图时间轴。
- `outputs/video1/ViralScope_report.md` 已基于新生成的 40 张截图补过一版人工分析内容。
- `ViralScope_AI_PRD.md` 已同步更新三段式抽帧规则。
- Git 仓库已初始化，并完成首个提交。

## 已验证达标的证据

- 已运行命令: `python main.py video1`
- 实际生成截图数: 40 张
- 实际时间点:
  `0.0s, 0.5s, 1.0s, 1.5s, 2.0s, 2.5s, 3.0s, 4.0s, 5.0s, 6.0s, 7.0s, 8.0s, 9.0s, 10.0s, 11.0s, 12.0s, 13.0s, 14.0s, 15.0s, 17.0s, 19.0s, 21.0s, 23.0s, 25.0s, 27.0s, 29.0s, 31.0s, 33.0s, 35.0s, 37.0s, 39.0s, 41.0s, 43.0s, 45.0s, 47.0s, 49.0s, 51.0s, 53.0s, 55.0s, 57.0s`
- 报告文件: `outputs/video1/ViralScope_report.md`
- 报告已包含:
  - 基础信息
  - 截图时间轴
  - 爆款核心原因
  - Hook 拆解
  - 内容结构拆解
  - 产品卖点与用户痛点
  - 评论区与转化线索
  - 可复用脚本模板
  - 优化建议
  - 转化诊断初步判断
  - 达人反馈话术

## 已知问题

- `samples/video1.json` 目前仍是空 demo 数据:
  - `category`、`product_type`、`target_audience`、`campaign_type`、`title`、`speech_summary` 为空。
  - `creator_profile` 各字段为空。
  - `metrics` 仍是 0 或空字符串。
  - `operator_note` 为空。
- 因为 JSON 数据未更新，当前报告里的基础信息、评论区判断、转化判断不能当作真实业务结论。
- 当前 `outputs/video1/ViralScope_report.md` 的分析部分是基于截图人工补写的，不是通过 AI API 自动生成。
- 当前视频画面判断的主线是 Logitech G 直播设备组合，至少包含 Litra Beam LX、Yeti GX、G715；后续 JSON 需要和真实视频内容对齐。

## 下一步待办

- 补齐 `samples/video1.json` 的真实 demo 数据，包括类目、产品类型、目标人群、投放背景、标题、口播摘要、达人画像和指标数据。
- 口播摘要采用人工处理: 不接入自动 ASR pipeline 到代码里，视频用剪映/网页转写工具/本地 whisper 命令辅助转写，人工誊抄摘要到 JSON 的 `speech_summary` 字段。这是已确认的架构决定，不再作为待讨论项。
- 把报告里的优化建议按 PRD 第 9 节结构整理:
  - 可以直接照搬的 3 个点
  - 可以做得更好的 2 个点
  - 适合我们账号的落地版本
- Day 2 接入 AI 分析生成流程，但要保留当前不依赖 AI 的本地闭环作为兜底。
- 开始规划工具 2: 转化诊断模块，重点处理高播放低成交的视频。
- 每完成一个里程碑后更新本文件，避免忘记当前进度和未补数据。

## 2026-07-06 最新进度追加

### 已完成

- `samples/video1.json` 已补入真实 demo 基础信息:
  - 类目: `3c`
  - 产品类型: `logitech`
  - 目标人群: `streamer`
  - 投放类型: `竞品分析`
  - 标题、口播摘要、达人画像、播放/点赞/评论/收藏/分享、运营备注已填写。
- 已新增 `analyze_video.py`，AI 调用已收敛为 OpenAI-compatible API:
  - 支持官方 OpenAI API
  - 支持企业中转 / OpenAI-compatible 网关
- OpenAI-compatible API 已支持企业中转:
  - `openai_base_url`
  - `openai_model`
  - API key 读取 `OPENAI_API_KEY`
- Gemini provider 已移除，不再作为 Demo 测试路径。
- AI 报告固定输出到:
  - `outputs/video1/report_openai.md`
- `main.py` 已接入 AI 分析流程: 抽帧 -> 生成时间轴报告 -> 调用 `analyze_video.py`。
- `outputs/video1/ViralScope_report.md` 已基于更新后的 JSON 和截图重新补过一版人工分析结果。

### 关键帧策略当前状态

- 关键帧选择逻辑已改为基于已抽帧自动选择，不再手动写死时间点。
- 当前规则:
  - 0-3 秒: 已抽帧全部保留。
  - 3-15 秒: 已抽帧每隔 2 帧选 1 张。
  - 15 秒之后: 已抽帧每隔 2 帧选 1 张。
- 当前 `video1` 实际选中 24 张:
  `0.0s, 0.5s, 1.0s, 1.5s, 2.0s, 2.5s, 3.0s, 4.0s, 6.0s, 8.0s, 10.0s, 12.0s, 14.0s, 17.0s, 21.0s, 25.0s, 29.0s, 33.0s, 37.0s, 41.0s, 45.0s, 49.0s, 53.0s, 57.0s`
- 注意: 24 张可能高于原先预期的 12-15 张，后续如需控制成本，需要继续压缩 15 秒后的选帧密度。

### 当前卡点

- 项目路径仍是 `D:\新建文件夹`。
- 已尝试改名为 `D:\viralscope-ai`，但 `Rename-Item`、`Move-Item`、`cmd /c ren` 都返回 `Access is denied`。
- 当前确认没有发生部分移动，原目录仍完整存在。
- 后续建议:
  - 关闭 VS Code、PowerShell、资源管理器等可能占用目录的程序。
  - 用管理员权限在资源管理器中手动改名，或用 `robocopy` 复制到 `D:\viralscope-ai` 后再切换路径。

### API 实测状态

- `openai` Python 包已安装成功。
- OpenAI/企业中转实测卡在环境变量读取:
  - 终端中曾出现 `echo $env:OPENAI_API_KEY` 可以看到 `sk-`。
  - 但运行项目时仍出现 `OpenAI 调用失败: 缺少环境变量 OPENAI_API_KEY`。
- 当前判断: VS Code / PowerShell / Python 实际运行环境可能不一致，后续需要在同一个终端里执行:
  - `echo $env:OPENAI_API_KEY`
  - `python -c "import os; print(os.getenv('OPENAI_API_KEY'))"`
  - `python main.py video1`
- Gemini 已决定不再接入；后续只验证 OpenAI / OpenAI-compatible 中转。

### 下一步

- 先把当前代码和进度提交存档。
- 之后优先解决运行环境变量问题，确认 Python 进程能读到 `OPENAI_API_KEY`。
- 再跑 OpenAI-compatible API 生成:
  - `outputs/video1/report_openai.md`
- 验收报告质量，重点看:
  - 是否引用具体时间点。
  - 是否区分流量原因和转化原因。
  - 翻拍建议是否能直接给达人执行。
  - 是否编造不存在的数据。

## 技术决策记录

- OpenAI SDK直连企业中转会被拦截(报错"Your request was blocked"),已改为用requests.post直接调用/chat/completions端点,绕过SDK的这个限制。后续如果换环境或换中转服务商,优先检查这个问题。
- 关键帧数量:24张会导致请求超时,已压缩到14张,可作为后续视频的关键帧数量上限参考(如果视频更长,建议维持在12-15张区间,不要超过20张)。
- video1.json的真实数据已补齐(播放748k/点赞3873/评论34/收藏1071/转发54/订单0),对应视频是Logitech G主播设备种草视频。

## 当前状态更新

- 工具1核心闭环已完整跑通:抽帧->真实数据填充->AI分析(OpenAI企业中转)->三段式翻拍建议报告生成
- 报告质量已达标:时间点引用密度高,流量/转化原因区分清晰,三段式建议结构正确。

## 2026-07-07 今日进度

### 已完成

- 已恢复并切换到干净 Git 工作区:
  - 当前主工作目录: `E:\viral-scope-checkout`
  - 原 `E:\viral-scope` 是无 Git 的复制目录，不再作为主要开发目录。
- AI 调用链路已实测跑通:
  - `python main.py video1` 可完成抽帧和基础时间轴报告。
  - OpenAI SDK 调企业中转会被拦截，已改为 `requests.post` 直接调用 `/chat/completions`。
  - `outputs/video1/report_openai.md` 已由 OpenAI-compatible 企业中转生成。
- 关键帧输入已从 24 张压缩到 14 张:
  - 当前规则: 0-3 秒全部保留，3-15 秒每 4 张选 1 张，15 秒后每 6 张选 1 张。
  - `video1` 当前 AI 输入帧:
    `0.0s, 0.5s, 1.0s, 1.5s, 2.0s, 2.5s, 3.0s, 4.0s, 8.0s, 12.0s, 17.0s, 29.0s, 41.0s, 53.0s`
- 已完成工具 2: 转化诊断模块:
  - 新增 `diagnose.py`
  - 读取 `outputs/{video_name}/report_openai.md`
  - 读取 `samples/{video_name}.json` 的 `metrics`
  - 复用 `analyze_video.py` 的 OpenAI-compatible 调用逻辑
  - 输出 `outputs/{video_name}/diagnosis.md`
- 已生成 `video1` 转化诊断报告:
  - 文件: `outputs/video1/diagnosis.md`
  - 结论聚焦在购买决策卡点，输出了一句话诊断、三条优先动作和达人反馈话术。
- 已完成静态展示页:
  - 新增 `generate_showcase.py`
  - 支持 `python generate_showcase.py <video_name>`
  - 动态读取 JSON、`report_openai.md`、`diagnosis.md` 和 `frames/`
  - 输出 `outputs/{video_name}/showcase.html`
  - `video1` 展示页已生成: `outputs/video1/showcase.html`
- 核心脚本已参数化:
  - `python main.py <video_name>`
  - `python diagnose.py <video_name>`
  - `python generate_showcase.py <video_name>`
  - 核心脚本内已清理 `video1` / `VIDEO_NAME` 硬编码。

### 当前完整 Demo 流程

1. 准备文件:
   - `samples/{video_name}.mp4`
   - `samples/{video_name}.json`
2. 运行工具 1:
   - `python main.py <video_name>`
3. 运行工具 2:
   - `python diagnose.py <video_name>`
4. 生成展示页:
   - `python generate_showcase.py <video_name>`
5. 打开:
   - `outputs/{video_name}/showcase.html`

### 当前输出文件规范

- 本地基础时间轴报告: `outputs/{video_name}/ViralScope_report.md`
- AI 爆款拆解报告: `outputs/{video_name}/report_openai.md`
- 转化诊断报告: `outputs/{video_name}/diagnosis.md`
- 静态展示页: `outputs/{video_name}/showcase.html`

## 2026-07-07 优化重构

### 关键帧逻辑重构

- 新增 `frames.py`，作为帧工具的唯一实现: `frame_time` / `list_frames` / `pick_keyframes`。
  - `frame_time` 正则改为 `frame_([\d.]+)s\.jpg`，兼容任意小数位（原 `\d+\.\d` 只认一位小数）。
  - 选帧逻辑从「取模 `%4`/`%6`」改为「按目标时间点选最近帧」:
    `TARGET_TIMES = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 5.0, 8.0, 12.0, 18.0, 30.0, 45.0, 60.0]`。
    超出视频长度的目标点自动跳过，天然把关键帧控制在 <=14 张、可解释、不超时。
  - `video1` 实测选出 13 张: `0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 5.0, 8.0, 12.0, 17.0, 29.0, 45.0`。
- `analyze_video.py` / `build_timeline.py` / `generate_showcase.py` 删除各自的 `frame_time` 副本，统一从 `frames` import。

### 报告与展示页统一改为全英文

- `analyze_video.py`（SYSTEM_PROMPT + build_user_prompt）与 `diagnose.py`（DIAGNOSIS_PROMPT）正文语言改为英文，
  面向海外达人可直接复制发送。
- 章节标题也从中文改为英文（报告 `## 6. Repeatable Viral Formula` / `### Our Brand Version` 等，
  诊断 `## 1.~## 4.`）。
- 展示页 `showcase.html` 的所有 UI 文案（板块标题、指标标签、副标题、图片 alt、CSS 注释）全部改为英文，
  页面已无残留中文（`video1` 实测零 CJK）。
- 兼容性: `extract_section` 和 `diagnosis_section_index` 同时匹配中/英标题，
  因此旧的中文标题报告无需重跑 API 也能正常渲染成英文页面。
- 注意 1: 重新运行 `main.py` / `diagnose.py` 会让 `.md` 报告的标题也变英文（消耗一次 API），但非必需。
- 注意 2: 展示页副标题会回显 JSON 里的 `category`/`product_type`/`target_audience` 原值；
  若这些字段填的是中文（如 `video2.json` 的 美妆/修容棒/女性），副标题会出现中文——这是输入数据，非代码问题。

### 展示页重写（generate_showcase.py）

- 去掉逐帧猜测文案的 `time_insight` / `timeline_html`（原展示页的主要「乱」源）。
- 改为清晰四段式，标题中文 / 正文英文:
  1. Hero + 核心指标
  2. 关键帧概览（只放缩略图 + 时间戳，不再逐帧编故事）
  3. ✅ 值得复制的部分（绿）: 可复制爆款公式 + 适合我们账号的落地版本
  4. ⚠️ 需要优化的部分（橙）: 转化诊断优先动作 + 给达人的建议
- 新增 `extract_section(report_text, keyword)`: 按 markdown 标题抽取版块正文（到下一个同级/更高级标题为止）。
- 新增 `markdown_block_to_html`: 保留标题 / 有序列表 / 无序列表 / 段落 / 加粗 / 行内 code 结构，不再压成单句。

### 文件漏洞与缺失修复

- `.gitignore`: 新增 `outputs/`（生成产物）和 `config.json`（本地私有配置，含中转地址）;
  已执行 `git rm -r --cached outputs/` 和 `git rm --cached config.json` 停止追踪（磁盘文件保留）。
- `extract_frames.py`:
  - ffmpeg / ffprobe 改为优先 `shutil.which()` 走系统 PATH（跨平台），本地 `ffmpeg-bin/*.exe` 仅作 Windows 兜底。
  - 精确抽帧: `-ss` 从 `-i` 之前移到之后，避免 0.5 秒粒度下的关键帧对齐偏差。
- 新增 `README.md`（定位 + 流程图 + 环境准备 + 运行命令 + 输出说明）。
- 新增 `requirements.txt`（`requests`）。
- 新增 `config.example.json`（指向 `https://api.openai.com/v1`，key 走 `OPENAI_API_KEY` 环境变量）。

### 待办 / 注意

- 公开仓库前需确认 `.git` 历史已重建或清洗，避免旧提交里保留本地私有配置。
- 英文报告已用新版 API prompt 重跑；GitHub Pages 展示副本位于 `docs/`。
