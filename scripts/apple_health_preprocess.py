#!/usr/bin/env python3
import argparse
import csv
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime
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

DATE_FORMAT = "%Y-%m-%d %H:%M:%S %z"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preprocess Apple Health export data into CSV files."
    )
    parser.add_argument(
        "--input", required=True, help="Path to Apple Health export.xml or export.zip"
    )
    parser.add_argument(
        "--output", required=True, help="Directory for generated CSV files"
    )
    parser.add_argument(
        "--types",
        default=",".join(sorted(SUPPORTED_TYPES)),
        help="Comma-separated output types, e.g. heart_rate,step_count,sleep_analysis",
    )
    return parser.parse_args()


def parse_requested_types(raw_types: str) -> list[str]:
    requested = [item.strip() for item in raw_types.split(",") if item.strip()]
    invalid = [item for item in requested if item not in SUPPORTED_TYPES]
    if invalid:
        raise ValueError(f"Unsupported types: {', '.join(sorted(invalid))}")
    return requested


def resolve_input_xml(
    input_path: Path,
) -> tuple[Path, tempfile.TemporaryDirectory[str] | None]:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if input_path.suffix.lower() == ".xml":
        return input_path, None

    if input_path.suffix.lower() != ".zip":
        raise ValueError("Input must be export.xml or export.zip")

    temp_dir = tempfile.TemporaryDirectory(prefix="apple-health-zip-")
    with zipfile.ZipFile(input_path) as zf:
        zf.extractall(temp_dir.name)

    possible_paths = [
        Path(temp_dir.name) / "apple_health_export" / "export.xml",
        Path(temp_dir.name) / "export.xml",
    ]
    for path in possible_paths:
        if path.exists():
            return path, temp_dir

    temp_dir.cleanup()
    raise FileNotFoundError("export.xml not found inside zip archive")


def ensure_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def safe_attr(element: ET.Element, key: str) -> str:
    return element.get(key, "")


def duration_minutes(start: str, end: str) -> str:
    if not start or not end:
        return ""
    try:
        start_dt = datetime.strptime(start, DATE_FORMAT)
        end_dt = datetime.strptime(end, DATE_FORMAT)
    except ValueError:
        return ""
    return str(int((end_dt - start_dt).total_seconds() / 60))


def collect_quantity_rows(root: ET.Element, type_identifier: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for record in root.findall("Record"):
        if safe_attr(record, "type") != type_identifier:
            continue
        rows.append(
            [
                safe_attr(record, "sourceName"),
                safe_attr(record, "startDate"),
                safe_attr(record, "endDate"),
                safe_attr(record, "value"),
                safe_attr(record, "unit"),
            ]
        )
    return rows


def collect_sleep_rows(root: ET.Element) -> list[list[str]]:
    rows: list[list[str]] = []
    for record in root.findall("Record"):
        if safe_attr(record, "type") != "HKCategoryTypeIdentifierSleepAnalysis":
            continue
        start = safe_attr(record, "startDate")
        end = safe_attr(record, "endDate")
        rows.append(
            [
                safe_attr(record, "sourceName"),
                start,
                end,
                SLEEP_STAGE_MAP.get(
                    safe_attr(record, "value"),
                    safe_attr(record, "value")
                    .replace("HKCategoryValueSleepAnalysis", "")
                    .lower(),
                ),
                duration_minutes(start, end),
            ]
        )
    return rows


def collect_workout_rows(root: ET.Element) -> list[list[str]]:
    rows: list[list[str]] = []
    for workout in root.findall("Workout"):
        rows.append(
            [
                safe_attr(workout, "sourceName"),
                safe_attr(workout, "startDate"),
                safe_attr(workout, "endDate"),
                WORKOUT_TYPE_MAP.get(
                    safe_attr(workout, "workoutActivityType"),
                    safe_attr(workout, "workoutActivityType")
                    .replace("HKWorkoutActivityType", "")
                    .lower(),
                ),
                safe_attr(workout, "duration"),
                safe_attr(workout, "totalEnergyBurned"),
                safe_attr(workout, "totalDistance"),
            ]
        )
    return rows


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
    temp_dir: tempfile.TemporaryDirectory[str] | None = None

    try:
        requested_types = parse_requested_types(args.types)
        xml_path, temp_dir = resolve_input_xml(input_path)
        ensure_output_dir(output_dir)
        root = ET.parse(xml_path).getroot()

        for output_name in requested_types:
            if output_name in QUANTITY_TYPES:
                write_csv(
                    output_dir / f"{output_name}.csv",
                    ["source_name", "start_date", "end_date", "value", "unit"],
                    collect_quantity_rows(root, QUANTITY_TYPES[output_name]),
                )
            elif output_name == "sleep_analysis":
                write_csv(
                    output_dir / "sleep_analysis.csv",
                    [
                        "source_name",
                        "start_date",
                        "end_date",
                        "sleep_stage",
                        "duration_minutes",
                    ],
                    collect_sleep_rows(root),
                )
            elif output_name == "workouts":
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
                    collect_workout_rows(root),
                )

        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
