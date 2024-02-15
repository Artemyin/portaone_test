import bz2
from typing import Generator, List
from collections.abc import Callable
import time
import sys
import operator as op
from pathlib import Path


def data_stream_from_file(
    file_name: Path,
    processor: Callable
) -> Generator[bytes, None, None]:  # [yield, send, return]
    with processor(file_name, "rb") as f:
        for line in f:
            yield line


def cast_to_int(data: bytes) -> int:
    return int(data.decode('utf-8').strip())


def mediana(lst: List[int], length: int) -> int | float:
    mid_index = length // 2
    if length % 2 == 0:  # Even length
        return (lst[mid_index - 1] + lst[mid_index]) / 2
    return lst[mid_index]


def average(summ: int, length: int) -> int | float:
    return summ / length


def max_number(numbers_list: List[int]) -> int:
    return numbers_list[-1]


def min_number(numbers_list: List[int]) -> int:
    return numbers_list[0]


def sort_numbers(numbers_list: List[int]) -> List[int]:
    return sorted(numbers_list)


def find_cons_seq(changes: str) -> Generator[int | None, int | bool, None]:
    ops = {
        "increase": {"then": op.lt, "equal": op.ge},
        "decrease": {"then": op.gt, "equal": op.le}
    }
    highest_seq = 0
    current_seq = 0
    prev_number = None
    while True:
        number = yield None
        if not (number or highest_seq):
            continue
        if not number and highest_seq:
            yield highest_seq
        if prev_number and ops[changes]["then"](prev_number, number):
            current_seq += 1
        if not prev_number:
            prev_number = number
        if prev_number and ops[changes]["equal"](prev_number, number):
            current_seq = 1
        if current_seq > highest_seq:
            highest_seq = current_seq
        prev_number = number


def get_processor(filename: Path) -> Callable:
    text_processors = {'.bz2': bz2.open, '.txt': open}
    file_type = filename.suffix
    processor = text_processors.get(file_type) or text_processors.get('.txt')
    return processor


def get_data_stream(filename):
    processor = get_processor(filename)
    return data_stream_from_file(filename, processor)


def calculate_statistic(filename: Path, skip: bool) -> dict:
    numbers_list = []
    summ = 0
    hi_gen = find_cons_seq("increase")
    low_gen = find_cons_seq("decrease")
    next(hi_gen)
    next(low_gen)
    try:
        data_stream = get_data_stream(filename)  # "10m.txt.bz2"
    except OSError as e:
        raise OSError(f"Cant open such file {filename}: ") from e
    for data in data_stream:
        try:
            number = cast_to_int(data)
        except ValueError as e:
            if not skip:
                raise ValueError(f"Cant process given value {data}:") from e

        numbers_list.append(number)
        summ += number
        hi_gen.send(number)
        low_gen.send(number)
        
    if not numbers_list:
        raise ValueError("empty file")
    
    increase_seq = hi_gen.send(False)
    decrease_seq = low_gen.send(False)
    numbers_list = sort_numbers(numbers_list)
    maximum = max_number(numbers_list)
    minimum = min_number(numbers_list)
    avg = average(summ, len(numbers_list))
    medn = mediana(numbers_list, len(numbers_list))

    result = {
        "maximum": maximum, "minimum": minimum, "average": avg, "mediana": medn,
        "increase_seq": increase_seq, "decrease_seq": decrease_seq
    }
    return result


def main(args) -> None:
    filename = Path(args.filename)
    skip = args.skip
    show_time = args.show_time

    start_time = time.time()

    try:
        res = calculate_statistic(filename, skip)
        end_time = time.time()
        execution_time = end_time - start_time

        print(f"Maximum value: {res.get('maximum')}")
        print(f"Minimum value: {res.get('minimum')}")
        print(f"Average: {res.get('average'):.3f}")
        print(f"Mediana: {res.get('mediana')}")
        print(f"Sequence that increase: {res.get('increase_seq')}")
        print(f"Sequence that decrease: {res.get('decrease_seq')}")

        if show_time:
            print(f"Execution time is {execution_time:.3f}")
    except Exception as e:
        print("Occur unexpected error: \n", e)
        sys.exit()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog='statistic counter',
        description="""
            This programm find the maximum & minimum number
            in the file,
            the median, average arithmetic,
            the largest increasing sequence,
            the largest decreasing sequence
        """,
        epilog='Written by Artemii'
    )

    parser.add_argument(
        'filename',
        help='file with set of integers,\
            tested only with .bz2 and .txt,\
            but can consume other file types'
    )
    parser.add_argument(
        '-st', '--show_time',
        action='store_true',
        help='show execution timer'
    )
    parser.add_argument(
        '-s', '--skip',
        action='store_true',
        help='skip bad values in set'
    )
    args = parser.parse_args()

    main(args)
