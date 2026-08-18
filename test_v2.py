import subprocess
import sys
import unittest
from pathlib import Path
from main import read_data, generate_biography

DIR = Path(__file__).parent
DATA = DIR / "ZebraID_V2_Natural_Data.txt"

class TestV2(unittest.TestCase):
    def test_100_items_in_each_external_section(self):
        data = read_data(DATA)
        for section, values in data.items():
            self.assertEqual(len(values), 100, section)

    def test_no_placeholders_remain(self):
        for _ in range(100):
            result = generate_biography(DATA)
            self.assertNotRegex(result, r"\[[A-Z_]+\]")

    def test_output_is_long_first_person_bio(self):
        result = generate_biography(DATA)
        self.assertTrue(result.startswith("I'm ") or result.startswith("My name's "))
        self.assertGreater(len(result), 250)

    def test_100_calls_vary(self):
        results = [generate_biography(DATA) for _ in range(100)]
        print(f"\n100 calls produced {len(set(results))} unique biographies.")
        self.assertGreater(len(set(results)), 1)

    def test_restart_sequences_differ(self):
        command = [sys.executable, "main.py", "--count", "10"]
        first = subprocess.check_output(command, cwd=DIR, text=True)
        second = subprocess.check_output(command, cwd=DIR, text=True)
        self.assertNotEqual(first, second)

    def test_prompt_comes_after_bio(self):
        prompt = "What should I do this weekend?"
        result = subprocess.check_output(
            [sys.executable, "main.py", "--prompt", prompt],
            cwd=DIR,
            text=True
        )
        self.assertIn(prompt, result)
        self.assertGreater(result.index(prompt), 200)

if __name__ == "__main__":
    unittest.main(verbosity=2)
