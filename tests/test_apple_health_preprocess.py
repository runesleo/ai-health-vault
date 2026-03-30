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
