import csv
import importlib.util
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "apple_health_preprocess.py"
FIXTURE = ROOT / "tests" / "fixtures" / "apple_health_export.xml"


class AppleHealthPreprocessTests(unittest.TestCase):
    def load_script_module(self):
        spec = importlib.util.spec_from_file_location("apple_health_preprocess", SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def build_cmd(self, output_dir: Path, *extra_args: str) -> list[str]:
        return [
            "python3",
            str(SCRIPT),
            "--input",
            str(FIXTURE),
            "--output",
            str(output_dir),
            *extra_args,
        ]

    def run_script(self, *extra_args: str) -> tuple[subprocess.CompletedProcess[str], Path]:
        output_dir = Path(tempfile.mkdtemp(prefix="apple-health-out-"))
        cmd = self.build_cmd(output_dir, *extra_args)
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

    def test_main_uses_streaming_xml_parser(self) -> None:
        module = self.load_script_module()
        output_dir = Path(tempfile.mkdtemp(prefix="apple-health-out-"))
        args = module.argparse.Namespace(
            input=str(FIXTURE),
            output=str(output_dir),
            types="heart_rate,step_count,sleep_analysis,workouts",
        )

        with (
            mock.patch.object(module, "parse_args", return_value=args),
            mock.patch.object(
                module.ET,
                "parse",
                side_effect=AssertionError("ET.parse should not be used"),
            ),
        ):
            result = module.main()

        self.assertEqual(result, 0)

    def test_refuses_to_delete_existing_nonempty_output_dir(self) -> None:
        output_dir = Path(tempfile.mkdtemp(prefix="apple-health-nonempty-out-"))
        sentinel = output_dir / "keep.txt"
        sentinel.write_text("do not delete", encoding="utf-8")

        result = subprocess.run(
            self.build_cmd(output_dir, "--types", "heart_rate"),
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(sentinel.exists())


if __name__ == "__main__":
    unittest.main()
