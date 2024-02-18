import unittest
import os
from unittest.mock import patch
from argparse import Namespace
import bz2
from contextlib import redirect_stdout
from io import StringIO

from unittest_parametrize import parametrize, ParametrizedTestCase

from statistics_counter import calculate_statistic, main


class TestCalculateStatistic(ParametrizedTestCase):
    @parametrize(
        "data_stream,expected",
        [
            (
                [5, 1, 3, 4, 1],
                {
                    "maximum": 5,
                    "minimum": 1,
                    "average": 2.8,
                    "mediana": 3.0,
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
                    "mediana": 5.0,
                    "increase_seq": 4,
                    "decrease_seq": 1,
                },
            ),
        ],
        ids=["one", "two"],
    )
    @patch("statistics_counter.cast_to_int")
    def test_calculate_statistic(self, mock_cast_to_int, data_stream, expected):
        # Mock cast_to_int to return the same value
        mock_cast_to_int.side_effect = lambda x: x
        actual_results = calculate_statistic(data_stream, True)
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
        self.assertRaises(OSError, main, self.args)

    @parametrize(
        "file_content",
        [(b"",), (b"a\nb\nc",), (b"1\n\n2\n2",), (b"1,\n2",), (b"1\n1.2\n2",)],
        ids=[
            "empty_file",
            "without_digits",
            "with_empty_strings",
            "with_punctuation_mark",
            "with_float",
        ],
    )
    def test_raise_error_read_files(self, file_content):
        with open("test_file.txt", "wb") as f:
            f.write(file_content)
        self.assertRaises(SystemExit, main, self.args)


class TestMainFunction(unittest.TestCase):
    args = Namespace()
    # Set values for the attributes
    args.skip = False
    args.show_time = False

    def test_main_function_open_bz2_output(self):
        # Data to be compressed
        data = "1"  # Using newline characters for clarity
        # Open the file for writing in binary mode, with compression
        with bz2.open("test_file.txt.bz2", "wb") as compressed_file:
            compressed_file.write(data.encode())
        self.args.filename = "test_file.txt.bz2"

        with redirect_stdout(StringIO()) as captured_output:
            main(self.args)  # Call the main function with appropriate args
            output = captured_output.getvalue().strip()

        expected_results = (
            "Maximum value: 1\n"
            "Minimum value: 1\n"
            "Average: 1.0\n"
            "Mediana: 1.0\n"
            "Sequence that increase: 1\n"
            "Sequence that decrease: 1"
        )
        # main(self.args)
        os.remove("test_file.txt.bz2")
        self.assertEqual(output, expected_results)

    def test_main_function_open_txt_output(self):
        # Data to be compressed
        data = "1"  # Using newline characters for clarity
        # Open the file for writing in binary mode, with compression
        with open("test_file.txt", "wb") as file:
            file.write(data.encode())
        self.args.filename = "test_file.txt"

        with redirect_stdout(StringIO()) as captured_output:
            main(self.args)  # Call the main function with appropriate args
            output = captured_output.getvalue().strip()

        expected_results = (
            "Maximum value: 1\n"
            "Minimum value: 1\n"
            "Average: 1.0\n"
            "Mediana: 1.0\n"
            "Sequence that increase: 1\n"
            "Sequence that decrease: 1"
        )
        # main(self.args)
        os.remove("test_file.txt")
        self.assertEqual(output, expected_results)


if __name__ == "__main__":
    unittest.main()
