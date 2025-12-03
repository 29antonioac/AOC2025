import os
from pathlib import Path

import polars as pl
import typer
from elf import (
    get_puzzle_input,
    submit_puzzle_answer,
    get_private_leaderboard,
    get_user_status,
    OutputFormat,
)
from elf.helpers import parse_input, read_input, timer
from rich.console import Console

pl.Config.set_tbl_rows(20)
pl.Config.set_tbl_cols(20)
pl.Config.set_fmt_str_lengths(200)
pl.Config.set_fmt_table_cell_list_len(20)

YEAR = 2025
DAY = int(Path(__file__).parent.name.split("day")[-1])
LEADERBOARD = os.getenv("BOARD_ID")

console = Console()

DIAL_SIZE = 100

@timer()
def part1(input_data: list[str]) -> str:
    df = pl.DataFrame(
        {"line": input_data}
    ).with_row_index().lazy().with_columns(
        pl.col("line").str.split("").cast(pl.List(pl.Int32)).alias("digits")
    ).with_columns(
        pl.col("digits").list.slice(0, pl.col("digits").list.len() - 1).list.explode().cum_max().implode().over("index").alias("first_digits"),
    ).with_columns(
        pl.col("digits").list.slice(pl.col("first_digits").list.arg_max() + 1).list.explode().cum_max().implode().over("index").alias("second_digits")
    ).with_columns(
        pl.concat_str(
            pl.col("first_digits").list.max(),
            pl.col("second_digits").list.max(),
        ).cast(pl.Int32).alias("joltage")
    ).sort("index").collect()

    console.print(df)
    result = df.select(pl.sum("joltage").cast(pl.String)).item()

    return result

@timer()
def part2(input_data: list[str]) -> str:

    joltage_len = 12

    df = pl.DataFrame(
        {"line": input_data}
    ).with_row_index().lazy().with_columns(
        pl.col("line").str.split("").cast(pl.List(pl.Int32)).alias("digits")
    ).with_columns(
        pl.col("digits").list.slice(
            0, 
            pl.col("digits").list.len() - (joltage_len - 1)
        ).list.explode().cum_max().implode().over("index").alias("first_digits"),
    ).with_columns(
        (pl.col("digits").list.len() - (joltage_len - 2)).alias("second_length"),
        (pl.min_horizontal(pl.col("digits").list.len() - (joltage_len - 2), pl.col("digits").list.len() - joltage_len - 1 -  pl.col("first_digits").list.arg_max() + 2)).alias("second_length_corrected"),
        pl.col("digits").list.slice(
            pl.col("first_digits").list.arg_max() + 1, 
            (pl.min_horizontal(pl.col("digits").list.len() - (joltage_len - 2), pl.col("digits").list.len() - joltage_len - 1 -  (pl.col("first_digits").list.arg_max()) + 2)),
        ).list.explode().cum_max().implode().over("index").alias("second_digits")
    ).with_columns(
        pl.col("digits").list.slice(
            pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + 2, 
            (pl.min_horizontal(pl.col("digits").list.len() - (joltage_len - 3), pl.col("digits").list.len() - joltage_len - 1 -  (pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max()) + 2))
        ).list.explode().cum_max().implode().over("index").alias("third_digits")
    ).with_columns(
        pl.col("digits").list.slice(
            pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max() + 3,
            (pl.min_horizontal(pl.col("digits").list.len() - (joltage_len - 4), pl.col("digits").list.len() - joltage_len - 1 -  (pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max()) + 2))
        ).list.explode().cum_max().implode().over("index").alias("fourth_digits")
    ).with_columns(
        pl.col("digits").list.slice(
            pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max() + pl.col("fourth_digits").list.arg_max() + 4,
            (pl.min_horizontal(pl.col("digits").list.len() - (joltage_len - 5), pl.col("digits").list.len() - joltage_len - 1 -  (pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max() + pl.col("fourth_digits").list.arg_max()) + 2))
        ).list.explode().cum_max().implode().over("index").alias("fifth_digits")
    ).with_columns(
        pl.col("digits").list.slice(
            pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max() + pl.col("fourth_digits").list.arg_max() + pl.col("fifth_digits").list.arg_max() + 5,
            (pl.min_horizontal(pl.col("digits").list.len() - (joltage_len - 6), pl.col("digits").list.len() - joltage_len - 1 -  (pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max() + pl.col("fourth_digits").list.arg_max() + pl.col("fifth_digits").list.arg_max()) + 2))
        ).list.explode().cum_max().implode().over("index").alias("sixth_digits")
    ).with_columns(
        pl.col("digits").list.slice(
            pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max() + pl.col("fourth_digits").list.arg_max() + pl.col("fifth_digits").list.arg_max() + pl.col("sixth_digits").list.arg_max() + 6,
            (pl.min_horizontal(pl.col("digits").list.len() - (joltage_len - 7), pl.col("digits").list.len() - joltage_len - 1 -  (pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max() + pl.col("fourth_digits").list.arg_max() + pl.col("fifth_digits").list.arg_max() + pl.col("sixth_digits").list.arg_max()) + 2))
        ).list.explode().cum_max().implode().over("index").alias("seventh_digits")
    ).with_columns(
        pl.col("digits").list.slice(
            pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max() + pl.col("fourth_digits").list.arg_max() + pl.col("fifth_digits").list.arg_max() + pl.col("sixth_digits").list.arg_max() + pl.col("seventh_digits").list.arg_max() + 7,
            (pl.min_horizontal(pl.col("digits").list.len() - (joltage_len - 8), pl.col("digits").list.len() - joltage_len - 1 -  (pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max() + pl.col("fourth_digits").list.arg_max() + pl.col("fifth_digits").list.arg_max() + pl.col("sixth_digits").list.arg_max() + pl.col("seventh_digits").list.arg_max()) + 2))
        ).list.explode().cum_max().implode().over("index").alias("eigth_digits")
    ).with_columns(
        pl.col("digits").list.slice(
            pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max() + pl.col("fourth_digits").list.arg_max() + pl.col("fifth_digits").list.arg_max() + pl.col("sixth_digits").list.arg_max() + pl.col("seventh_digits").list.arg_max() + pl.col("eigth_digits").list.arg_max() + 8,
            (pl.min_horizontal(pl.col("digits").list.len() - (joltage_len - 9), pl.col("digits").list.len() - joltage_len - 1 -  (pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max() + pl.col("fourth_digits").list.arg_max() + pl.col("fifth_digits").list.arg_max() + pl.col("sixth_digits").list.arg_max() + pl.col("seventh_digits").list.arg_max() + pl.col("eigth_digits").list.arg_max()) + 2))
        ).list.explode().cum_max().implode().over("index").alias("nineth_digits")
    ).with_columns(
        pl.col("digits").list.slice(
            pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max() + pl.col("fourth_digits").list.arg_max() + pl.col("fifth_digits").list.arg_max() + pl.col("sixth_digits").list.arg_max() + pl.col("seventh_digits").list.arg_max() + pl.col("eigth_digits").list.arg_max() + pl.col("nineth_digits").list.arg_max() + 9,
            (pl.min_horizontal(pl.col("digits").list.len() - (joltage_len - 10), pl.col("digits").list.len() - joltage_len - 1 -  (pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max() + pl.col("fourth_digits").list.arg_max() + pl.col("fifth_digits").list.arg_max() + pl.col("sixth_digits").list.arg_max() + pl.col("seventh_digits").list.arg_max() + pl.col("eigth_digits").list.arg_max() + pl.col("nineth_digits").list.arg_max()) + 2))
        ).list.explode().cum_max().implode().over("index").alias("tenth_digits")
    ).with_columns(
        pl.col("digits").list.slice(
            pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max() + pl.col("fourth_digits").list.arg_max() + pl.col("fifth_digits").list.arg_max() + pl.col("sixth_digits").list.arg_max() + pl.col("seventh_digits").list.arg_max() + pl.col("eigth_digits").list.arg_max() + pl.col("nineth_digits").list.arg_max() + pl.col("tenth_digits").list.arg_max() + 10,
            (pl.min_horizontal(pl.col("digits").list.len() - (joltage_len - 11), pl.col("digits").list.len() - joltage_len - 1 -  (pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max() + pl.col("fourth_digits").list.arg_max() + pl.col("fifth_digits").list.arg_max() + pl.col("sixth_digits").list.arg_max() + pl.col("seventh_digits").list.arg_max()+  pl.col("eigth_digits").list.arg_max() + pl.col("nineth_digits").list.arg_max() + pl.col("tenth_digits").list.arg_max()) + 2))
        ).list.explode().cum_max().implode().over("index").alias("eleventh_digits")
    ).with_columns(
        pl.col("digits").list.slice(
            pl.col("first_digits").list.arg_max() + pl.col("second_digits").list.arg_max() + pl.col("third_digits").list.arg_max() + pl.col("fourth_digits").list.arg_max() + pl.col("fifth_digits").list.arg_max() + pl.col("sixth_digits").list.arg_max() + pl.col("seventh_digits").list.arg_max() + pl.col("eigth_digits").list.arg_max() + pl.col("nineth_digits").list.arg_max() + pl.col("tenth_digits").list.arg_max() + pl.col("eleventh_digits").list.arg_max() + 11
        ).list.explode().cum_max().implode().over("index").alias("twelveth_digits")
    ).with_columns(
        pl.concat_str(
            pl.col("first_digits").list.max(),
            pl.col("second_digits").list.max(),
            pl.col("third_digits").list.max(),
            pl.col("fourth_digits").list.max(),
            pl.col("fifth_digits").list.max(),
            pl.col("sixth_digits").list.max(),
            pl.col("seventh_digits").list.max(),
            pl.col("eigth_digits").list.max(),
            pl.col("nineth_digits").list.max(),
            pl.col("tenth_digits").list.max(),
            pl.col("eleventh_digits").list.max(),
            pl.col("twelveth_digits").list.max(),
        ).cast(pl.Int64).alias("joltage")
    ).sort("index").collect()

    console.print(df)
    result = df.select(pl.sum("joltage").cast(pl.String)).item()

    return result


def main(submit: bool = False):

    part_functions = [part1, part2]

    day_input = parse_input(get_puzzle_input(YEAR, DAY))
    # print(day_input)

    test_input = parse_input(read_input(Path("test_input.txt")))
    # print(test_input)

    for idx, part in enumerate(part_functions):
        console.print()
        console.print(f"Checking part {idx+1}")
        test_result = part(test_input)
        console.print(f"Part {idx+1} Test Result: {test_result}")

        result = part(day_input)
        console.print(f"Part {idx+1} Result: {result}")

        if submit:
            submission_result = submit_puzzle_answer(YEAR, DAY, idx+1, result)
            console.print(submission_result.is_correct, submission_result.message)

if __name__ == "__main__":
    typer.run(main)