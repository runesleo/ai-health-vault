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
- `--output` 必须指向一个新目录或空目录，脚本不会删除你现有目录里的内容
- 如果你当前环境无法运行脚本，再退回到让 AI 临时生成兜底脚本
