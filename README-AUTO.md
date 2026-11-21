# 十二维灵感日历自动版
网站： https://jocyc-dev.github.io/twelve-inspirations/

## 一次性安装（不要上传 ZIP 本身）
将本压缩包里所有文件和文件夹的**内容**上传到 GitHub 仓库根目录，覆盖原来的 index.html、sw.js、manifest.webmanifest 和 icon.svg。
必须保持 `.github/workflows/daily.yml`、`scripts/generate.py`、`data/issues.json` 这几层路径结构；GitHub Upload files 支持拖入多个文件，但空目录不会自动保存，可将解压后的文件夹内容从文件管理器拖入并检查路径。如果网页上传丢失目录，请用 GitHub 网页新建文件并输入完整路径来创建。

然后在仓库 Settings → Secrets and variables → Actions → New repository secret：
Name = OPENAI_API_KEY
Secret = 你在 https://platform.openai.com/api-keys 创建的 API 密钥
不要把密钥贴给任何人，不要提交进仓库。

仓库 Actions → 每日自动发布十二维 → Run workflow → Run workflow，测试首次运行。
运行成功后，GitHub 会新增/更新 data/issues.json；网站刷新后出现新日期。
定时：北京时间21:13（UTC 13:13），GitHub Actions 定时可能延后；并非保证精准到分钟。
GitHub Pages 保持 main / (root) 即可，提交 data/issues.json 后自动更新。

## 重要限制
- 这**不会读取**你原有 ChatGPT 定时任务的输出，而是在 GitHub 另行调用付费 API 生成新的内容。
- ChatGPT Plus 不包含 API 计费额度；要先在 OpenAI API 账户配置支付方式并设置消费上限。
- AI 未必能准确核实所有外部事实。新闻只从公开RSS获取线索；未核验日期或原始报道时应注明。
- 每次生成如不满12项，脚本拒绝提交，避免缺栏。失败可通过 Actions 手动重试，已存在的日期不会覆盖。
- 首页预置的2026-11-19~21仍只是摘要，不是之前聊天里的完整原文。
- 使用的免费GitHub Pages仓库目前为公开仓库，自动写入的文章也公开。
