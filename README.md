# Test Task Description

The task involves a script named `statistics_counter.py` which is designed to solve the following tasks:

1. Find the maximum number in the file.
2. Find the minimum number in the file.
3. Calculate the median.
4. Calculate the average arithmetic value.
5. *(Optional)* Find the largest consecutive sequence of numbers that increases.
6. *(Optional)* Find the largest consecutive sequence of numbers that decreases.

This repository contains:

- `statistics_counter.py`: The main working script.
- `test.py`: Unit tests that cover basic use cases.
- `Dockerfile`: Instructions on how to build a Docker image.

## Usage Instructions

### Option 1

1. Install Python 3.11 or higher (tested only on this version).
2. Download the `statistics_counter.py` script.
3. Run the script using the command `$ python3.11 statistics_counter.py path/file.txt`.
4. You can try to make the script executable by following instructions like [this](https://stackoverflow.com/a/27762412/16608168).

For Linux, you can use this approach to increase usability:

```bash
$ sudo cp statistics_counter.py /usr/local/bin
$ chmod +x 755 /usr/local/bin/statistics_counter.py
$ statistics_counter.py -h
```

Now you can run the script from anywhere.

### Option 2

Download the Docker image from the provided source.
```BASH
docker pull artemyin/numbers-set-analyzer-app:v1.0
```
To execute the script, run the following commands:

```bash
$ export FILE=name_of_your_file
$ docker run -v path/$FILE:/app/$FILE artemyin/numbers-set-analyzer-app:v1.0 /app/$FILE
```

**Important**: You must pass the absolute path to your document. We have to mount a volume to the Docker image with the desired document.

### Usage Instruction

When you run the script without passing any argument, it will show you basic script info and an error notice that a file is required.

```bash
$ statistics_counter.py
usage: statistic counter [-h] [-st] [-s] filename
statistic counter: error: the following arguments are required: filename
```

To see detailed help, use the `-h` argument.

```bash
$ statistics_counter.py -h
usage: statistic counter [-h] [-st] [-s] filename

This program finds the maximum & minimum number in the file, the median, average arithmetic,
the largest increasing sequence, the largest decreasing sequence

positional arguments:
  filename          file with set of integers, tested only with .bz2 and .txt, but can
                    consume other file types

options:
  -h, --help        show this help message and exit
  -st, --show_time  show execution timer
  -s, --skip        skip bad values in set

Written by Artemii
```

The script takes one positional argument `filename`, which could be a path to a file or a filename. The program works with files that have the format .txt or .bz2, but you can try to pass other file formats. 
```bash
$ statistics_counter.py code/portaone/10m.txt.bz2 -st
Maximum value: 49999978
Minimum value: -49999996
Average: 7364.4
Mediana: 25216
Sequence that increase: 10
Sequence that decrease: 11
Execution time is 15.816892
```

As you can see, I've added extra options:

- `--show_time` or `-st` adds an extra line at the end of calculations that shows how much time the execution of the script took.
- `--skip` or `-s` allows the script to skip values which can't be interpreted as integers and continue calculating without stopping the program.

## Implementation Details

The program was written in a way that makes it easy to maintain and test each function separately. It was initially written using a simple list and standard sorting, and due to its modularity, a custom sorting method could be added in the future.

The entry point to the script is:

```python
if __name__ == "__main__":
     import argparse
     parser = argparse.ArgumentParser(...)
     parser.add_argument(...)
     ...
     args = parser.parse_args()
     main(args)
```


Using `argparse`, command-line arguments passed into the `main()` function.

Inside the `main()` function, arguments are unpacked and the file path is passed into the `get_data_stream()` function.

```python
# Intentionaly omited some code, for simplify explanation
def main(args) -> None:
    # Unpacking comand line arguments
    filename = Path(args.filename)
    try:
        # Get Iterator from generator function that read file line by line
        data_stream = get_data_stream(filename)
        # passing iterator to calculate statistic
        res = calculate_statistic(data_stream)
        print(res)  # Simplified; Print calculation result. 
    except OSError as e:
        raise OSError(f"Cant open such file {filename}: ") from e
    except Exception as e:
        print("Occur unexpected error: \n", e)
        sys.exit()
```
 Function `get_data_stream()` analyzes the file extension and accordingly chooses how to read the file in the `get_processor()` function and returns a function for reading file.  The generator function `data_stream_from_file()` creates an generator that reads the document line by line (this allows the document to not be fully loaded into RAM.) and returns iterator into `data_stream` variable in `main()`

If you want, you could modify the `data_stream_from_file()` or `get_processor()` functions to add custom readers.

```python
def get_data_stream(filename: Path) -> Generator:
    processor = get_processor(filename)
    return data_stream_from_file(filename, processor)

def get_processor(filename: Path) -> Callable:
    text_processors = {".bz2": bz2.open, ".txt": open}
    file_type = filename.suffix
    processor = text_processors.get(file_type) or text_processors.get(".txt")
    return processor

def data_stream_from_file(
    file_name: Path, processor: Callable
) -> Generator[bytes, None, None]:  # [yield, send, return]
    with processor(file_name, "rb") as f:
        for line in f:
            yield line
```


All calculations occur within `calculate_statistic()`. It takes the generator `data_stream`, which is iterated over in a `for` loop. It tries to cast the string to an integer `number = cast_to_int(data)`, adds the value to the list `numbers_list.append(number)`, and simultaneously calculates the sum of all numbers for calculating the average arithmetic value and passes values into generator functions for sequence calculations.

When the loop iteration is complete, the list is sorted `numbers_list = sort_numbers(numbers_list)`. From the sorted list, the median is calculated `medn = mediana(numbers_list, len(numbers_list))` as well as the maximum and minimum numbers, which are obtained from the first and last elements of the sorted list. 

The average arithmetic value is calculated from the sum of all numbers obtained during the loop iteration and the length of the list. 

The results of the generator functions for the increasing and decreasing sequences are obtained by passing False, what is signal to return calculated result `increase_seq = hi_gen.send(False)`, `decrease_seq = low_gen.send(False)`.

The obtained results from calculations are stored in a dictionary and returned to the `main()` function where they are printed.

```python
def calculate_statistic(data_stream: Generator, skip: bool) -> dict:
    numbers_list = []
    summ = 0
    hi_gen = find_cons_seq("increase")
    low_gen = find_cons_seq("decrease")
    next(hi_gen)
    next(low_gen)
    for data in data_stream:
        try:
            number = cast_to_int(data)
        except ValueError as e:
            raise ValueError(f"Cant process given value {data}:") from e

        numbers_list.append(number)

        summ += number
        hi_gen.send(number)
        low_gen.send(number)

    if not numbers_list:
        raise ValueError("empty file")

    numbers_list = sort_numbers(numbers_list)
    maximum = max_number(numbers_list)
    minimum = min_number(numbers_list)
    avg = average(summ, len(numbers_list))
    medn = mediana(numbers_list, len(numbers_list))
    increase_seq = hi_gen.send(False)
    decrease_seq = low_gen.send(False)

    result = {
        "maximum": maximum,
        "minimum": minimum,
        "average": avg,
        "mediana": medn,
        "increase_seq": increase_seq,
        "decrease_seq": decrease_seq,
    }
    return result
```

The most interesting solution is considered to be the `find_cons_seq()` function for calculating the longest sequence, which is made in the form of a generator function that allowed local variables to be stored throughout the entire loop. During initialization `hi_gen = find_cons_seq("increase")` we pass the value `"increase"` or `"decrease"` for the increasing and decreasing sequence respectively. Inside the function is a dictionary that contains comparison functions, which are selected during function initialization what allow use just one function for two cases.

New values inside the loop are passed through `hi_gen.send(number)`. When the for loop has been finished, passing the value `False` signals the return of the final calculated value `increase_seq = hi_gen.send(False)`.

```python
def find_cons_seq(changes: str) -> Generator[int | None, int | bool, None]:
    # dict with comparing functions that allow use one function instead two
    # type of sequence passing with initializing generator
    ops = {
        "increase": {"then": op.lt, "equal": op.ge},
        "decrease": {"then": op.gt, "equal": op.le},
    }
    highest_seq = 0
    current_seq = 0
    prev_number = None
    while True:
        number = yield None
        # skip first loop at initialization
        if not (number or highest_seq):
            continue
        # if sent False to number return result
        if not number and highest_seq:
            yield highest_seq
        if not prev_number:
            prev_number = number
        # if current higher | less  than previus namber than increment counter
        # for increasing and decreasing sequence respectivly 
        if ops[changes]["then"](prev_number, number):
            current_seq += 1
        # if equal or [less | higher] reset counter   
        if ops[changes]["equal"](prev_number, number):
            current_seq = 1
        # reasign highest sequence
        if current_seq > highest_seq:
            highest_seq = current_seq
        prev_number = number
```

## Unit Tests

Some unit tests have been added. 

If you want to run them, you have to install the `unittest_parametrize` module:
```BASH
$ pip install unittest_parametrize
```
To run tests: 
```BASH
$ python -m unittest -v
```
Implemented next tests:

```python
test_calculate_statistic()  # For test adecuate calculations.
```

```python 
test_raise_error_read_files()  # For test error handling files with wrong data.
``` 
```python 
test_main_function_open_bz2_output()  # For test proper reading bz2 compresed files.
``` 
```python 
test_main_function_open_txt_output()  # For test proper reading txt files.
```