import unittest
import os
from unittest.mock import patch
from pathlib import Path
from argparse import Namespace

from statistics_counter import calculate_statistic, main

from unittest_parametrize import parametrize, ParametrizedTestCase


class TestCalculateStatistic(ParametrizedTestCase):
    @parametrize(
        "mock_data_stream,expected",
        [
            (
                [5, 1, 3, 4, 1],
                {
                    "maximum": 5,
                    "minimum": 1,
                    "average": 2.8,
                    "mediana": 3,
                    "increase_seq": 3,
                    "decrease_seq": 2,
                },
            ),
            (
                [2, 4, 6, 8],
                {
                    "maximum": 8,
                    "minimum": 2,
                    "average": 5.0,
                    "mediana": 5,
                    "increase_seq": 4,
                    "decrease_seq": 1,
                },
            ),
        ],
        ids=["one", "two"],
    )
    @patch("statistics_counter.get_data_stream")
    @patch("statistics_counter.cast_to_int")
    def test_calculate_statistic(
        self, mock_cast_to_int, mock_get_data_stream, mock_data_stream, expected
    ):
        mock_get_data_stream.return_value = mock_data_stream

        # Mock cast_to_int to return the same value
        mock_cast_to_int.side_effect = lambda x: x

        filename = Path("test_file.txt")  # Placeholder filename for the test
        actual_results = calculate_statistic(filename, True)

        self.assertEqual(actual_results, expected)


class TestFileReading(ParametrizedTestCase):
    args = Namespace()
    # Set values for the attributes
    args.filename = "test_file.txt"
    args.skip = False
    args.show_time = False

    def tearDown(self):
        # Clean up the test file
        try:
            os.remove("test_file.txt")
        except FileNotFoundError:
            print("file for test hasnt been created")

    def test_raise_error_open_files(self):
        self.assertRaises(SystemExit, main, self.args)

    @parametrize(
        "file_content",
        [(b"",), (b"a\nb\nc",), (b"1\n\n2\n2",), (b"1,\n2",)],
        ids=[
            "empty_file",
            "without_digits",
            "with_empty_strings",
            "with_punctuation_mark",
        ],
    )
    def test_raise_error_read_files(self, file_content):
        with open("test_file.txt", "wb") as f:
            f.write(file_content)
        self.assertRaises(SystemExit, main, self.args)


if __name__ == "__main__":
    unittest.main()
