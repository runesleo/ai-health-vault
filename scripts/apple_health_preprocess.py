#!/usr/bin/env python3
import argparse
import contextlib
import csv
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

OUTPUT_HEADERS = {
    "heart_rate": ["source_name", "start_date", "end_date", "value", "unit"],
    "resting_heart_rate": ["source_name", "start_date", "end_date", "value", "unit"],
    "walking_heart_rate_average": [
        "source_name",
        "start_date",
        "end_date",
        "value",
        "unit",
    ],
    "heart_rate_variability_sdnn": [
        "source_name",
        "start_date",
        "end_date",
        "value",
        "unit",
    ],
    "oxygen_saturation": ["source_name", "start_date", "end_date", "value", "unit"],
    "vo2max": ["source_name", "start_date", "end_date", "value", "unit"],
    "step_count": ["source_name", "start_date", "end_date", "value", "unit"],
    "sleep_analysis": [
        "source_name",
        "start_date",
        "end_date",
        "sleep_stage",
        "duration_minutes",
    ],
    "workouts": [
        "source_name",
        "start_date",
        "end_date",
        "workout_type",
        "duration_minutes",
        "total_energy_kcal",
        "total_distance_km",
    ],
}

QUANTITY_TYPE_BY_IDENTIFIER = {
    type_identifier: output_name
    for output_name, type_identifier in QUANTITY_TYPES.items()
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
        "--output",
        required=True,
        help="New or empty directory for generated CSV files",
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
        if not output_dir.is_dir():
            raise NotADirectoryError(f"Output path is not a directory: {output_dir}")
        if any(output_dir.iterdir()):
            raise FileExistsError(
                f"Output directory must be empty or not exist: {output_dir}"
            )
        return
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


def build_quantity_row(record: ET.Element) -> list[str]:
    return [
        safe_attr(record, "sourceName"),
        safe_attr(record, "startDate"),
        safe_attr(record, "endDate"),
        safe_attr(record, "value"),
        safe_attr(record, "unit"),
    ]


def build_sleep_row(record: ET.Element) -> list[str]:
    start = safe_attr(record, "startDate")
    end = safe_attr(record, "endDate")
    raw_value = safe_attr(record, "value")
    return [
        safe_attr(record, "sourceName"),
        start,
        end,
        SLEEP_STAGE_MAP.get(
            raw_value,
            raw_value.replace("HKCategoryValueSleepAnalysis", "").lower(),
        ),
        duration_minutes(start, end),
    ]


def build_workout_row(workout: ET.Element) -> list[str]:
    raw_type = safe_attr(workout, "workoutActivityType")
    return [
        safe_attr(workout, "sourceName"),
        safe_attr(workout, "startDate"),
        safe_attr(workout, "endDate"),
        WORKOUT_TYPE_MAP.get(
            raw_type,
            raw_type.replace("HKWorkoutActivityType", "").lower(),
        ),
        safe_attr(workout, "duration"),
        safe_attr(workout, "totalEnergyBurned"),
        safe_attr(workout, "totalDistance"),
    ]


def get_writer(
    output_name: str,
    output_dir: Path,
    stack: contextlib.ExitStack,
    writers: dict[str, csv.writer],
) -> csv.writer:
    writer = writers.get(output_name)
    if writer is not None:
        return writer

    file_handle = stack.enter_context(
        (output_dir / f"{output_name}.csv").open("w", newline="", encoding="utf-8")
    )
    writer = csv.writer(file_handle)
    writer.writerow(OUTPUT_HEADERS[output_name])
    writers[output_name] = writer
    return writer


def write_requested_csvs(
    xml_path: Path, output_dir: Path, requested_types: list[str]
) -> None:
    requested_set = set(requested_types)
    writers: dict[str, csv.writer] = {}
    root: ET.Element | None = None
    element_stack: list[ET.Element] = []

    with contextlib.ExitStack() as stack:
        context = ET.iterparse(xml_path, events=("start", "end"))
        for event, elem in context:
            if event == "start":
                element_stack.append(elem)
                if root is None:
                    root = elem
                continue

            is_direct_child = root is not None and len(element_stack) == 2
            if is_direct_child and elem.tag == "Record":
                record_type = safe_attr(elem, "type")
                quantity_output = QUANTITY_TYPE_BY_IDENTIFIER.get(record_type)
                if quantity_output in requested_set:
                    get_writer(quantity_output, output_dir, stack, writers).writerow(
                        build_quantity_row(elem)
                    )
                elif (
                    record_type == "HKCategoryTypeIdentifierSleepAnalysis"
                    and "sleep_analysis" in requested_set
                ):
                    get_writer("sleep_analysis", output_dir, stack, writers).writerow(
                        build_sleep_row(elem)
                    )
            elif is_direct_child and elem.tag == "Workout" and "workouts" in requested_set:
                get_writer("workouts", output_dir, stack, writers).writerow(
                    build_workout_row(elem)
                )

            element_stack.pop()
            if is_direct_child and root is not None:
                root.clear()
            else:
                elem.clear()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output).expanduser().resolve()
    temp_dir: tempfile.TemporaryDirectory[str] | None = None

    try:
        requested_types = parse_requested_types(args.types)
        xml_path, temp_dir = resolve_input_xml(input_path)
        ensure_output_dir(output_dir)
        write_requested_csvs(xml_path, output_dir, requested_types)

        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
