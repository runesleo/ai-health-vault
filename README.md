# AI Health Vault

**English** | [中文](README_CN.md)

Build a private, AI-powered health management system for yourself and your family using Obsidian.

Not an app. Not a code project. It's a set of **templates + prompts + setup guides**. Clone it, let your AI (Claude / ChatGPT / Gemini) read it, and it will guide you through building your family's health archive step by step.

## Why

- Medical reports scattered across hospitals — no one tracks trends for you
- Your parents can't remember their own medication, dosages, or follow-up dates
- Commercial health apps require uploading your family's private health data
- You just need local templates where the data stays on your machine

## 30-Minute Setup

```
1. Fork this repo (or download ZIP)
2. Open the vault/ folder in Obsidian
3. Fill in family member names in "健康管理中心.md"
4. Take a photo of a medical report → send to AI → AI fills in the template
5. Done. Repeat step 4 for every checkup, doctor visit, or new medication.
```

## Quick Start: Claude Code Users

If you use [Claude Code](https://claude.ai/claude-code), just clone and start talking:

```bash
git clone https://github.com/runesleo/ai-health-vault.git
cd ai-health-vault
claude
# "Help me analyze this checkup report" (attach photo)
```

The `.claude/skills/` directory contains 8 pre-built skills that activate automatically — no manual prompt copy-paste needed.

## Repository Structure

```
ai-health-vault/
├── .claude/skills/                 # Claude Code skills (auto-loaded)
│   ├── health-report-extract.md    # Checkup report → structured data
│   ├── medication-recognize.md     # Pill box photo → drug info
│   ├── health-trend-analysis.md    # Multi-checkup trend analysis
│   ├── medical-visit-prep.md       # Pre-visit checklist generator
│   ├── apple-watch-analysis.md     # Apple Watch health data analysis
│   ├── family-friendly-health.md   # Plain language for parents
│   ├── checkup-calendar.md         # Follow-up calendar + alerts
│   └── daily-health-plan.md        # Personalized daily health plan
├── vault/                          # Obsidian Vault templates (ready to use)
│   ├── 健康管理中心.md              # Hub + workflow instructions
│   ├── 家庭成员健康档案.md           # Family overview
│   ├── 就医记录.md                  # Medical visits / surgery / chronic conditions
│   ├── 成员模板/
│   │   └── 体检档案-模板.md         # Per-person checkup archive (incl. Apple Watch)
│   ├── tracking/
│   │   ├── 用药打卡.csv             # Daily medication log
│   │   ├── 饮食记录.csv             # Diet tracking
│   │   ├── 运动记录.csv             # Exercise tracking
│   │   └── 体检指标.csv             # Key checkup metrics over time
│   └── 知识库/
│       ├── 常见指标参考.md           # Common health metrics reference
│       └── 推荐字段标准.md           # Recommended field naming standard
├── prompts/                        # Prompt collection (works with any AI)
│   ├── 01-体检报告提取.md            # Photo → structured data
│   ├── 02-药盒识别.md               # Medication photo → drug list
│   ├── 03-趋势分析.md               # Historical comparison + anomaly detection
│   ├── 04-就医准备.md               # Pre-visit checklist generator
│   ├── 05-Apple-Watch数据分析.md    # Health data export → analysis
│   ├── 06-微信版口语化.md            # Convert to plain language for parents
│   ├── 07-复查日历生成.md            # Follow-up calendar + overdue alerts
│   └── 08-日常管理方案.md            # Diet / exercise / medication / warning signs
├── guides/
│   └── 快速开始.md                  # Detailed setup tutorial
└── LICENSE
```

## Prompts

Each file in `prompts/` is a standalone prompt — copy-paste into any AI conversation:

| Prompt | Purpose | Input |
|--------|---------|-------|
| Checkup Report Extraction | Photo/PDF → structured table | Report photo |
| Medication Recognition | Pill box photo → drug name + dosage + frequency | Medication photo |
| Trend Analysis | Compare multiple checkups, flag anomalies | Checkup archive |
| Pre-Visit Prep | Generate questions for your doctor | Department + history |
| Apple Watch Analysis | Export health data → full report | export.zip |
| WeChat Version | Convert analysis to plain language for parents | Any analysis result |
| Follow-up Calendar | Generate follow-up schedule with overdue alerts | Family archives |
| Daily Health Plan | Diet + exercise + medication + warning signs | Personal archive |

If you want AI outputs to stay consistent across checkups, medications, medical visits, and Apple Watch imports, see `vault/知识库/推荐字段标准.md` for the recommended field naming standard.

## Who This Is For

- Tech-savvy people who want to build health archives for their parents
- Anyone who cares about health data but doesn't want to use third-party apps
- Apple Watch / smartband owners who want more value from their data

## Who This Is NOT For

- People who don't use AI tools (requires Claude / ChatGPT / Gemini)
- People who want fully automated solutions (this is a template — you feed data to AI)
- People who are fine with commercial health apps handling their data

## Privacy

All health data is stored locally in Obsidian — nothing is uploaded automatically. However, when you send data to AI for analysis, the content passes through their servers:

- **Claude Code (API mode)** — Anthropic does not use API inputs for model training ([privacy policy](https://www.anthropic.com/policies/privacy))
- **ChatGPT** — Turn off "Improve the model for everyone" in Settings → Data Controls
- **Gemini** — Check your data sharing settings in Google AI Studio
- **Maximum privacy** — Use a local model (e.g., Ollama, LM Studio) for analysis

> Obsidian is your local vault. AI is your analyst. The vault never leaves your machine — but the analysis step involves cloud APIs unless you use a local model.

## Contributing

Issues and PRs welcome:
- New prompts (e.g., specialized extraction for specific test types)
- Improve existing template structures
- Add reference ranges for common health metrics
- Translations

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=runesleo/ai-health-vault&type=Date)](https://star-history.com/#runesleo/ai-health-vault&Date)

## Author

Leo ([@runes_leo](https://x.com/runes_leo)) — AI × Crypto independent builder. Quantitative trading on Polymarket, building data analysis and automation systems with Claude Code. Shipping code, building products, documenting lessons learned. More → [leolabs.me](https://leolabs.me)

## License

MIT
