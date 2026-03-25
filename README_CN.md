# AI Health Vault

[English](README.md) | **中文**

用 AI + Obsidian 为自己和家人搭建私有化健康管理系统。

不是 App，不是代码项目——是一套**模板 + Prompt + 搭建指南**。Clone 下来，让你的 AI（Claude / ChatGPT / Gemini）读一遍，它就能指引你一步步搭好自己的家庭健康档案。

## 为什么需要这个

- 体检报告散落在各家医院，没人帮你汇总趋势
- 老人的病史、用药、复查时间，问他们自己都记不清
- 商用健康 App（蚂蚁阿福等）要上传你全家的隐私数据
- 你只需要一套本地运行的模板，数据完全属于你自己

## 30 分钟搭建流程

```
1. Fork 本仓库（或下载 ZIP）
2. 用 Obsidian 打开 vault/ 文件夹
3. 把家庭成员名字填入「健康管理中心.md」
4. 拍体检报告 → 发给 AI → AI 按模板填入档案
5. 完成。以后每次体检/看病/买药，重复第 4 步
```

## Claude Code 用户快速开始

如果你用 [Claude Code](https://claude.ai/claude-code)，clone 下来直接聊就行：

```bash
git clone https://github.com/runesleo/ai-health-vault.git
cd ai-health-vault
claude
# "帮我分析这份体检报告"（附上照片）
```

`.claude/skills/` 目录下有 8 个预置 Skill，自动加载，不用手动复制 Prompt。

## 仓库结构

```
ai-health-vault/
├── .claude/skills/               # Claude Code Skills（自动加载）
│   ├── health-report-extract.md  # 体检报告 → 结构化数据
│   ├── medication-recognize.md   # 药盒照片 → 药物信息
│   ├── health-trend-analysis.md  # 多次体检趋势分析
│   ├── medical-visit-prep.md     # 就医前清单生成
│   ├── apple-watch-analysis.md   # Apple Watch 数据分析
│   ├── family-friendly-health.md # 转成给父母看的版本
│   ├── checkup-calendar.md       # 复查日历 + 提醒
│   └── daily-health-plan.md      # 个性化日常健康方案
├── vault/                        # Obsidian Vault 模板（直接用）
│   ├── 健康管理中心.md             # 入口 Hub + 工作流说明
│   ├── 家庭成员健康档案.md          # 家庭总览
│   ├── 就医记录.md                 # 就医/手术/慢性病模板
│   ├── 成员模板/
│   │   └── 体检档案-模板.md        # 单人体检档案（含 Apple Watch 数据表）
│   ├── tracking/
│   │   ├── 用药打卡.csv            # 每日用药记录
│   │   ├── 饮食记录.csv            # 饮食追踪
│   │   ├── 运动记录.csv            # 运动追踪
│   │   └── 体检指标.csv            # 历次体检关键指标
│   └── 知识库/
│       └── 常见指标参考.md          # AI 生成的指标解读参考
├── prompts/                       # Prompt 集（喂给任何 AI 都能用）
│   ├── 01-体检报告提取.md           # 拍照 → 结构化数据
│   ├── 02-药盒识别.md              # 拍药盒 → 用药清单
│   ├── 03-趋势分析.md              # 历史对比 + 异常标注
│   ├── 04-就医准备.md              # 生成就医前清单
│   ├── 05-Apple-Watch数据分析.md   # 健康数据导出 → 分析
│   ├── 06-微信版口语化.md           # 转成给父母看的版本
│   ├── 07-复查日历生成.md           # 生成复查时间表 + 过期提醒
│   └── 08-日常管理方案.md           # 饮食/运动/用药/就医信号
├── guides/
│   ├── 快速开始.md                 # 详细搭建教程
│   └── FAQ.md                     # 常见问题
└── LICENSE
```

## Prompt 集说明

`prompts/` 里的每个文件都是独立的 Prompt，复制粘贴到任何 AI 对话里就能用：

| Prompt | 用途 | 输入 |
|--------|------|------|
| 体检报告提取 | 拍照/PDF → 结构化表格 | 体检报告照片 |
| 药盒识别 | 拍药盒 → 药名+剂量+频次 | 药盒照片 |
| 趋势分析 | 对比多次体检，标注异常趋势 | 体检档案.md |
| 就医准备 | 看病前生成问题清单 | 科室名 + 历史档案 |
| Apple Watch 数据分析 | 导出健康数据 → 完整分析报告 | export.zip |
| 微信版口语化 | 把分析结果转成父母能看懂的话 | 任意分析结果 |
| 复查日历生成 | 生成复查时间表，标注过期/即将到期项 | 全家档案 |
| 日常管理方案 | 饮食禁忌 + 运动建议 + 用药提醒 + 就医信号 | 个人档案 |

## 谁适合用

- 想给父母建健康档案的技术人
- 关注自己健康数据但不想用第三方 App 的人
- 有 Apple Watch / 智能手环，想让数据发挥更大价值的人

## 谁不适合

- 不用 AI 工具的人（需要 Claude / ChatGPT / Gemini 任一）
- 想要一键自动化的人（这是模板，需要你主动喂数据给 AI）
- 对隐私不敏感、商用 App 就够用的人

## 隐私说明

所有健康数据存储在本地 Obsidian 中，不会自动上传到任何地方。但当你把数据发给 AI 分析时，内容会经过 AI 服务商的服务器：

- **Claude Code（API 模式）** — Anthropic 不会将 API 输入用于模型训练
- **ChatGPT** — 建议在 设置 → 数据控制 中关闭"改进模型"
- **Gemini** — 检查 Google AI Studio 中的数据共享设置
- **最高隐私** — 使用本地模型（如 Ollama、LM Studio）进行分析

> Obsidian 是你的本地仓库，AI 是你的分析师。仓库永远不离开你的电脑——但分析这一步涉及云端 API，除非你使用本地模型。

## 贡献

欢迎提 Issue 和 PR：
- 新增 Prompt（比如针对特定检查项目的提取模板）
- 改进现有模板结构
- 补充常见指标的参考范围
- 翻译成其他语言

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=runesleo/ai-health-vault&type=Date)](https://star-history.com/#runesleo/ai-health-vault&Date)

## Author

Leo ([@runes_leo](https://x.com/runes_leo))，AI × Crypto 独立构建者。在 Polymarket 做量化交易，用 Claude Code 搭建数据分析和自动化系统。写代码、做产品、记踩坑。更多实战分享 → [leolabs.me](https://leolabs.me)

## License

MIT
