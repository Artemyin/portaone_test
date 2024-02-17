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

For Linux, you can use this approach:

```bash
$ sudo cp statistics_counter.py /usr/local/bin
$ chmod +x 755 /usr/local/bin/statistics_counter
```

Now you can run the script from anywhere.

### Option 2

Download the Docker image from the provided source.

To execute the script, run the following commands:

```bash
$ export FILE=name_of_your_file
$ docker run -v path/$FILE:/app/$FILE portaone:latest /app/$FILE
```

**Important**: You must pass the absolute path to your document. As we want to pass an external document into a Docker image, we have to mount a volume to the Docker image with the desired document.

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

The script takes one positional argument `filename`, which could be a path to a file or a filename. The program works with files that have the format .txt or .bz2, but you can try to pass other file formats. If you want, you could modify the `data_stream_from_file()` or `get_processor()` functions to add custom readers.

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

Using `argparse`, command-line arguments are parsed and passed into the `main()` function.

Inside the `main` function, arguments are unpacked and the file path is passed into the `get_data_stream()` function, which analyzes the file extension and accordingly chooses how to read the file in the `get_processor()` function. This function returns a function for reading the file into the generator function `data_stream_from_file()`, which creates an iterator `data_stream` that reads the document line by line. This allows the document to not be fully loaded into RAM.

All calculations occur within `calculate_statistic()`. It takes the generator `data_stream`, which is iterated over in a `for` loop. It tries to cast the string to an integer `number = cast_to_int(data)`, adds the value to the list `numbers_list.append(number)`, and simultaneously calculates the sum of all numbers for calculating the average arithmetic value. It also passes values into generator functions for sequence calculations.

When the loop iteration is complete, the list is sorted `numbers_list = sort_numbers(numbers_list)`. From the sorted list, the median is calculated `medn = mediana(numbers_list, len(numbers_list))` as well as the maximum and minimum numbers, which are obtained from the first and last elements of the sorted list. The average arithmetic value is calculated from the sum of all numbers obtained during the loop iteration and the length of the list. The results of the generator functions for the increasing and decreasing sequences are obtained `increase_seq = hi_gen.send(False)` `decrease_seq = low_gen.send(False)`.

The most interesting solution is considered to be the `find_cons_seq()` function for calculating the longest sequence, which is made in the form of a generator function that allowed local variables to be stored throughout the entire loop. During initialization `hi_gen = find_cons_seq("increase")` we pass the value `"increase"` or `"decrease"` for the increasing and decreasing sequence respectively. Inside the function is a dictionary that contains comparison functions, which are selected during function initialization.

New values inside the loop are passed through `hi_gen.send(number)`. When the loop has been passed, passing the value `False` signals the return of the final calculated value `increase_seq = hi_gen.send(False)`.

The obtained results are stored in a dictionary and returned to the `main` function where they are printed.

## Unit Tests

Some unit tests have been added. If you want to run them, you have to install the `statistics_counter` module.