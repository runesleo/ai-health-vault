# Apple Health Preprocess Script Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reusable Apple Health preprocessing script plus lightweight docs changes so users can convert `export.zip` or `export.xml` into stable CSV files before asking AI to analyze them.

**Architecture:** Implement one Python standard-library script under `scripts/` and one minimal XML fixture under `tests/fixtures/`. Use TDD with a small Python unittest suite that runs the script against the fixture and verifies CSV outputs. Then update the Apple Watch prompt, Claude skill, quick-start guide, and add a small `scripts/README.md` so the repo points to the script first and AI-generated scripts second.

**Tech Stack:** Python 3 standard library, unittest, argparse, csv, zipfile, tempfile, xml.etree.ElementTree, Markdown

---

### Task 1: Add The Failing Tests And Fixture

**Files:**
- Create: `tests/fixtures/apple_health_export.xml`
- Create: `tests/test_apple_health_preprocess.py`
- Test: `tests/test_apple_health_preprocess.py`

- [ ] **Step 1: Create the fixture directory and verify the test file does not exist**

Run:

```bash
mkdir -p /Users/zxnimac/.config/superpowers/worktrees/ai-health-vault/feat-apple-health-preprocess-script/tests/fixtures
test ! -f /Users/zxnimac/.config/superpowers/worktrees/ai-health-vault/feat-apple-health-preprocess-script/tests/test_apple_health_preprocess.py
```

Expected: exit code `0`

- [ ] **Step 2: Create the minimal Apple Health XML fixture**

Create `tests/fixtures/apple_health_export.xml` with:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<HealthData locale="en_US">
  <Record type="HKQuantityTypeIdentifierHeartRate" sourceName="Apple Watch" unit="count/min" creationDate="2026-03-01 08:10:00 +0800" startDate="2026-03-01 08:00:00 +0800" endDate="2026-03-01 08:00:00 +0800" value="62"/>
  <Record type="HKQuantityTypeIdentifierStepCount" sourceName="iPhone" unit="count" creationDate="2026-03-01 20:00:00 +0800" startDate="2026-03-01 00:00:00 +0800" endDate="2026-03-01 23:59:59 +0800" value="8450"/>
  <Record type="HKCategoryTypeIdentifierSleepAnalysis" sourceName="Apple Watch" unit="" creationDate="2026-03-02 07:05:00 +0800" startDate="2026-03-01 23:10:00 +0800" endDate="2026-03-02 06:40:00 +0800" value="HKCategoryValueSleepAnalysisAsleepCore"/>
  <Workout workoutActivityType="HKWorkoutActivityTypeWalking" duration="42" durationUnit="min" totalDistance="3.2" totalDistanceUnit="km" totalEnergyBurned="210" totalEnergyBurnedUnit="kcal" sourceName="Apple Watch" creationDate="2026-03-01 19:00:00 +0800" startDate="2026-03-01 18:00:00 +0800" endDate="2026-03-01 18:42:00 +0800"/>
</HealthData>
```

- [ ] **Step 3: Write the failing unittest suite**

Create `tests/test_apple_health_preprocess.py` with:

```python
import csv
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "apple_health_preprocess.py"
FIXTURE = ROOT / "tests" / "fixtures" / "apple_health_export.xml"


class AppleHealthPreprocessTests(unittest.TestCase):
    def run_script(self, *extra_args: str) -> tuple[subprocess.CompletedProcess[str], Path]:
        output_dir = Path(tempfile.mkdtemp(prefix="apple-health-out-"))
        cmd = [
            "python3",
            str(SCRIPT),
            "--input",
            str(FIXTURE),
            "--output",
            str(output_dir),
            *extra_args,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result, output_dir

    def test_generates_quantity_sleep_and_workout_csvs(self) -> None:
        result, output_dir = self.run_script()

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue((output_dir / "heart_rate.csv").exists())
        self.assertTrue((output_dir / "step_count.csv").exists())
        self.assertTrue((output_dir / "sleep_analysis.csv").exists())
        self.assertTrue((output_dir / "workouts.csv").exists())

    def test_quantity_csv_has_expected_headers(self) -> None:
        result, output_dir = self.run_script("--types", "heart_rate")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        with (output_dir / "heart_rate.csv").open(newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            headers = next(reader)

        self.assertEqual(
            headers,
            ["source_name", "start_date", "end_date", "value", "unit"],
        )

    def test_sleep_csv_has_expected_headers(self) -> None:
        result, output_dir = self.run_script("--types", "sleep_analysis")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        with (output_dir / "sleep_analysis.csv").open(newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            headers = next(reader)
            first_row = next(reader)

        self.assertEqual(
            headers,
            ["source_name", "start_date", "end_date", "sleep_stage", "duration_minutes"],
        )
        self.assertEqual(first_row[3], "asleep_core")

    def test_workout_csv_has_expected_headers(self) -> None:
        result, output_dir = self.run_script("--types", "workouts")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        with (output_dir / "workouts.csv").open(newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            headers = next(reader)
            first_row = next(reader)

        self.assertEqual(
            headers,
            [
                "source_name",
                "start_date",
                "end_date",
                "workout_type",
                "duration_minutes",
                "total_energy_kcal",
                "total_distance_km",
            ],
        )
        self.assertEqual(first_row[3], "walking")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run the tests to verify they fail**

Run:

```bash
cd /Users/zxnimac/.config/superpowers/worktrees/ai-health-vault/feat-apple-health-preprocess-script
python3 -m unittest tests/test_apple_health_preprocess.py -v
```

Expected: FAIL because `scripts/apple_health_preprocess.py` does not exist yet

- [ ] **Step 5: Commit the failing tests and fixture**

Run:

```bash
git add tests/fixtures/apple_health_export.xml tests/test_apple_health_preprocess.py
git commit -m "test: add apple health preprocess coverage"
```

### Task 2: Implement The Minimal Script

**Files:**
- Create: `scripts/apple_health_preprocess.py`
- Test: `tests/test_apple_health_preprocess.py`

- [ ] **Step 1: Create the scripts directory**

Run:

```bash
mkdir -p /Users/zxnimac/.config/superpowers/worktrees/ai-health-vault/feat-apple-health-preprocess-script/scripts
```

Expected: exit code `0`

- [ ] **Step 2: Write the minimal preprocessing script**

Create `scripts/apple_health_preprocess.py` with:

```python
#!/usr/bin/env python3
import argparse
import csv
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


QUANTITY_TYPES = {
    "heart_rate": "HKQuantityTypeIdentifierHeartRate",
    "resting_heart_rate": "HKQuantityTypeIdentifierRestingHeartRate",
    "walking_heart_rate_average": "HKQuantityTypeIdentifierWalkingHeartRateAverage",
    "heart_rate_variability_sdnn": "HKQuantityTypeIdentifierHeartRateVariabilitySDNN",
    "oxygen_saturation": "HKQuantityTypeIdentifierOxygenSaturation",
    "vo2max": "HKQuantityTypeIdentifierVO2Max",
    "step_count": "HKQuantityTypeIdentifierStepCount",
}

SPECIAL_TYPES = {"sleep_analysis", "workouts"}
SUPPORTED_TYPES = set(QUANTITY_TYPES) | SPECIAL_TYPES

SLEEP_STAGE_MAP = {
    "HKCategoryValueSleepAnalysisInBed": "in_bed",
    "HKCategoryValueSleepAnalysisAsleep": "asleep",
    "HKCategoryValueSleepAnalysisAsleepCore": "asleep_core",
    "HKCategoryValueSleepAnalysisAsleepDeep": "asleep_deep",
    "HKCategoryValueSleepAnalysisAsleepREM": "asleep_rem",
    "HKCategoryValueSleepAnalysisAwake": "awake",
}

WORKOUT_TYPE_MAP = {
    "HKWorkoutActivityTypeWalking": "walking",
    "HKWorkoutActivityTypeRunning": "running",
    "HKWorkoutActivityTypeCycling": "cycling",
    "HKWorkoutActivityTypeHiking": "hiking",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preprocess Apple Health export data into CSV files.")
    parser.add_argument("--input", required=True, help="Path to export.xml or export.zip")
    parser.add_argument("--output", required=True, help="Directory for generated CSV files")
    parser.add_argument(
        "--types",
        default=",".join(sorted(SUPPORTED_TYPES)),
        help="Comma-separated output types, e.g. heart_rate,step_count,sleep_analysis",
    )
    return parser.parse_args()


def resolve_input_xml(input_path: Path) -> tuple[Path, tempfile.TemporaryDirectory[str] | None]:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if input_path.suffix.lower() == ".xml":
        return input_path, None

    if input_path.suffix.lower() != ".zip":
        raise ValueError("Input must be export.xml or export.zip")

    temp_dir = tempfile.TemporaryDirectory(prefix="apple-health-zip-")
    with zipfile.ZipFile(input_path) as zf:
        zf.extractall(temp_dir.name)

    extracted_xml = Path(temp_dir.name) / "apple_health_export" / "export.xml"
    if not extracted_xml.exists():
        extracted_xml = Path(temp_dir.name) / "export.xml"

    if not extracted_xml.exists():
        temp_dir.cleanup()
        raise FileNotFoundError("export.xml not found inside zip archive")

    return extracted_xml, temp_dir


def parse_requested_types(raw_types: str) -> list[str]:
    requested = [item.strip() for item in raw_types.split(",") if item.strip()]
    invalid = [item for item in requested if item not in SUPPORTED_TYPES]
    if invalid:
        raise ValueError(f"Unsupported types: {', '.join(sorted(invalid))}")
    return requested


def ensure_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def collect_quantity_rows(root: ET.Element, type_identifier: str) -> list[list[str]]:
    rows = []
    for record in root.findall("Record"):
        if record.get("type") != type_identifier:
            continue
        rows.append([
            record.get("sourceName", ""),
            record.get("startDate", ""),
            record.get("endDate", ""),
            record.get("value", ""),
            record.get("unit", ""),
        ])
    return rows


def collect_sleep_rows(root: ET.Element) -> list[list[str]]:
    rows = []
    for record in root.findall("Record"):
        if record.get("type") != "HKCategoryTypeIdentifierSleepAnalysis":
            continue
        start = record.get("startDate", "")
        end = record.get("endDate", "")
        duration = duration_minutes(start, end)
        rows.append([
            record.get("sourceName", ""),
            start,
            end,
            SLEEP_STAGE_MAP.get(record.get("value", ""), record.get("value", "").replace("HKCategoryValueSleepAnalysis", "").lower()),
            duration,
        ])
    return rows


def collect_workout_rows(root: ET.Element) -> list[list[str]]:
    rows = []
    for workout in root.findall("Workout"):
        rows.append([
            workout.get("sourceName", ""),
            workout.get("startDate", ""),
            workout.get("endDate", ""),
            WORKOUT_TYPE_MAP.get(workout.get("workoutActivityType", ""), workout.get("workoutActivityType", "").replace("HKWorkoutActivityType", "").lower()),
            workout.get("duration", ""),
            workout.get("totalEnergyBurned", ""),
            workout.get("totalDistance", ""),
        ])
    return rows


def duration_minutes(start: str, end: str) -> str:
    from datetime import datetime

    if not start or not end:
        return ""

    fmt = "%Y-%m-%d %H:%M:%S %z"
    try:
        start_dt = datetime.strptime(start, fmt)
        end_dt = datetime.strptime(end, fmt)
    except ValueError:
        return ""

    return str(int((end_dt - start_dt).total_seconds() / 60))


def write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()

    try:
        requested_types = parse_requested_types(args.types)
        xml_path, temp_dir = resolve_input_xml(input_path)
        ensure_output_dir(output_dir)
        root = ET.parse(xml_path).getroot()

        for output_name in requested_types:
            if output_name in QUANTITY_TYPES:
                rows = collect_quantity_rows(root, QUANTITY_TYPES[output_name])
                write_csv(
                    output_dir / f"{output_name}.csv",
                    ["source_name", "start_date", "end_date", "value", "unit"],
                    rows,
                )
            elif output_name == "sleep_analysis":
                rows = collect_sleep_rows(root)
                write_csv(
                    output_dir / "sleep_analysis.csv",
                    ["source_name", "start_date", "end_date", "sleep_stage", "duration_minutes"],
                    rows,
                )
            elif output_name == "workouts":
                rows = collect_workout_rows(root)
                write_csv(
                    output_dir / "workouts.csv",
                    [
                        "source_name",
                        "start_date",
                        "end_date",
                        "workout_type",
                        "duration_minutes",
                        "total_energy_kcal",
                        "total_distance_km",
                    ],
                    rows,
                )

        if temp_dir is not None:
            temp_dir.cleanup()
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Run the focused tests to verify they pass**

Run:

```bash
cd /Users/zxnimac/.config/superpowers/worktrees/ai-health-vault/feat-apple-health-preprocess-script
python3 -m unittest tests/test_apple_health_preprocess.py -v
```

Expected: PASS, 4 tests

- [ ] **Step 4: Run one manual invocation for evidence**

Run:

```bash
cd /Users/zxnimac/.config/superpowers/worktrees/ai-health-vault/feat-apple-health-preprocess-script
rm -rf /tmp/apple-health-demo
python3 scripts/apple_health_preprocess.py --input tests/fixtures/apple_health_export.xml --output /tmp/apple-health-demo
find /tmp/apple-health-demo -maxdepth 1 -type f | sort
```

Expected: includes `heart_rate.csv`, `step_count.csv`, `sleep_analysis.csv`, `workouts.csv`

- [ ] **Step 5: Commit the script implementation**

Run:

```bash
git add scripts/apple_health_preprocess.py
git commit -m "feat: add apple health preprocess script"
```

### Task 3: Add Script Usage Docs And Update Apple Watch Guidance

**Files:**
- Create: `scripts/README.md`
- Modify: `prompts/05-Apple-Watch数据分析.md`
- Modify: `.claude/skills/apple-watch-analysis.md`
- Modify: `guides/快速开始.md`

- [ ] **Step 1: Create the script README**

Create `scripts/README.md` with:

```markdown
# Apple Health Scripts

## apple_health_preprocess.py

把 Apple Health 导出的 `export.zip` 或 `export.xml` 拆成多个 CSV，方便后续交给 AI 做趋势分析。

### 支持输入

- `export.zip`
- `export.xml`

### 当前输出

- `heart_rate.csv`
- `resting_heart_rate.csv`
- `walking_heart_rate_average.csv`
- `heart_rate_variability_sdnn.csv`
- `oxygen_saturation.csv`
- `vo2max.csv`
- `step_count.csv`
- `sleep_analysis.csv`
- `workouts.csv`

### 用法

```bash
python scripts/apple_health_preprocess.py --input /path/to/export.zip --output ./apple-health-csv
```

```bash
python scripts/apple_health_preprocess.py --input /path/to/export.xml --output ./apple-health-csv
```

```bash
python scripts/apple_health_preprocess.py --input /path/to/export.zip --output ./apple-health-csv --types heart_rate,step_count,sleep_analysis
```

### 说明

- 第一版只覆盖常用 Apple Health 数据类型，不是全量导出器
- 如果你当前环境无法运行脚本，再退回到让 AI 临时生成兜底脚本
```

- [ ] **Step 2: Update the prompt to prefer the repo script**

Replace the “让 AI 先写个脚本预处理” section in `prompts/05-Apple-Watch数据分析.md` with:

```markdown
优先做法：先运行仓库内脚本预处理。

```bash
python scripts/apple_health_preprocess.py --input /path/to/export.zip --output ./apple-health-csv
```

脚本会按常用数据类型拆分出独立 CSV（如心率、步数、睡眠、运动）。
你可以把这些 CSV 分批发给 AI 做进一步分析。

如果你当前环境没法运行脚本，再让 AI 现写一个兜底脚本：

```
这个 XML 文件太大了，请先帮我写一个 Python 脚本：
1. 解析 export.xml
2. 按数据类型（心率、步数、睡眠等）拆分成独立 CSV 文件
3. 每个 CSV 只保留：日期、时间、数值
这样我可以分批分析。
```
```

- [ ] **Step 3: Update the Claude skill to prefer the repo script**

Change the preprocessing steps and technical script section in `.claude/skills/apple-watch-analysis.md` to say:

```markdown
当用户提供 export.zip 时：
1. 优先使用仓库内脚本 `scripts/apple_health_preprocess.py`
2. 将 XML 按类型拆分为 CSV
3. 再按数据类型分批处理
4. 如果用户当前环境无法运行脚本，再临时提供 Python 兜底脚本
```

And replace the generic code block with:

```markdown
优先脚本：

```bash
python scripts/apple_health_preprocess.py --input /path/to/export.zip --output ./apple-health-csv
```

如果当前环境不能运行脚本，再提供临时 Python 兜底脚本。
```

- [ ] **Step 4: Update the quick-start FAQ**

Replace the Apple Health large-file answer in `guides/快速开始.md` with:

```markdown
Apple Watch 导出的 XML 可能超过 1GB。解决：
1. 先运行仓库内脚本：`python scripts/apple_health_preprocess.py --input /path/to/export.zip --output ./apple-health-csv`
2. 按数据类型（心率、步数、睡眠）拆分成独立 CSV
3. 分批喂给 AI 分析
4. 如果当前环境没法运行脚本，再让 AI 临时写一个兜底脚本
```

- [ ] **Step 5: Verify the docs reference the script path**

Run:

```bash
rg -n "scripts/apple_health_preprocess.py" /Users/zxnimac/.config/superpowers/worktrees/ai-health-vault/feat-apple-health-preprocess-script/prompts/05-Apple-Watch数据分析.md /Users/zxnimac/.config/superpowers/worktrees/ai-health-vault/feat-apple-health-preprocess-script/.claude/skills/apple-watch-analysis.md /Users/zxnimac/.config/superpowers/worktrees/ai-health-vault/feat-apple-health-preprocess-script/guides/快速开始.md /Users/zxnimac/.config/superpowers/worktrees/ai-health-vault/feat-apple-health-preprocess-script/scripts/README.md
```

Expected: matches in all four files

- [ ] **Step 6: Commit the docs changes**

Run:

```bash
git add scripts/README.md prompts/05-Apple-Watch数据分析.md .claude/skills/apple-watch-analysis.md guides/快速开始.md
git commit -m "docs: use apple health preprocess script in guides"
```

### Task 4: Final Verification

**Files:**
- Create: `scripts/apple_health_preprocess.py`
- Create: `scripts/README.md`
- Create: `tests/fixtures/apple_health_export.xml`
- Create: `tests/test_apple_health_preprocess.py`
- Modify: `prompts/05-Apple-Watch数据分析.md`
- Modify: `.claude/skills/apple-watch-analysis.md`
- Modify: `guides/快速开始.md`

- [ ] **Step 1: Run the full targeted test command again**

Run:

```bash
cd /Users/zxnimac/.config/superpowers/worktrees/ai-health-vault/feat-apple-health-preprocess-script
python3 -m unittest tests/test_apple_health_preprocess.py -v
```

Expected: PASS, 4 tests

- [ ] **Step 2: Verify the generated CSV headers from a fresh manual run**

Run:

```bash
cd /Users/zxnimac/.config/superpowers/worktrees/ai-health-vault/feat-apple-health-preprocess-script
rm -rf /tmp/apple-health-demo
python3 scripts/apple_health_preprocess.py --input tests/fixtures/apple_health_export.xml --output /tmp/apple-health-demo
for f in /tmp/apple-health-demo/*.csv; do echo "===== $f ====="; sed -n '1,3p' "$f"; done
```

Expected: CSV files with the planned headers and one data row in each populated file

- [ ] **Step 3: Review the final diff for scope**

Run:

```bash
git diff -- scripts/apple_health_preprocess.py scripts/README.md tests/fixtures/apple_health_export.xml tests/test_apple_health_preprocess.py prompts/05-Apple-Watch数据分析.md .claude/skills/apple-watch-analysis.md guides/快速开始.md
```

Expected: only script, tests, and Apple Health docs changes

- [ ] **Step 4: Make the final aggregation commit if needed**

Run:

```bash
git status --short
```

Expected: clean working tree or only intentionally untracked external files
