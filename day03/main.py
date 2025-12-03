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
    ).group_by("index", "digits").agg(
        pl.col("digits").list.slice(0, pl.col("digits").list.len() - 1).list.explode().cum_max().implode().alias("first_digits"),
    ).group_by("index", "digits", "first_digits").agg(
        pl.col("digits").list.slice(pl.col("first_digits").list.arg_max() + 1).list.explode().cum_max().implode().alias("second_digits")
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

        df = pl.DataFrame(
        {"line": input_data}
    ).with_row_index().lazy().with_columns(
        pl.col("line").str.split("").cast(pl.List(pl.Int32)).alias("digits")
    ).group_by("index", "digits").agg(
        pl.col("digits").list.slice(0, pl.col("digits").list.len() - 1).list.explode().cum_max().implode().alias("first_digits"),
    ).group_by("index", "digits", "first_digits").agg(
        pl.col("digits").list.slice(pl.col("first_digits").list.arg_max() + 1).list.explode().cum_max().implode().alias("second_digits")
    ).with_columns(
        pl.concat_str(
            pl.col("first_digits").list.max(),
            pl.col("second_digits").list.max(),
        ).cast(pl.Int32).alias("joltage")
    ).sort("index").collect()

    console.print(df)
    result = df.select(pl.sum("joltage").cast(pl.String)).item()

    return result

    # df = pl.DataFrame(
    #     {"line": input_data}
    # ).with_row_index().lazy().with_columns(
    #     pl.col("line").str.split("").cast(pl.List(pl.Int32)).alias("digits")
    # ).group_by("index", "digits").agg(
    #     pl.col("digits").list.slice(0, pl.col("digits").list.len() - 1).list.explode().cum_max().implode().alias("first_digits"),
    # ).group_by("index", "digits", "first_digits").agg(
    #     pl.col("digits").list.slice(pl.col("first_digits").list.arg_max() + 1).list.explode().cum_max().implode().alias("second_digits")
    # ).group_by("index", "digits", "first_digits", "second_digits").agg(
    #     pl.col("digits").list.slice(pl.col("first_digits").list.arg_max() + 1).list.explode().cum_max().implode().alias("second_digits")
    # ).group_by("index", "digits", "first_digits").agg(
    #     pl.col("digits").list.slice(pl.col("first_digits").list.arg_max() + 1).list.explode().cum_max().implode().alias("second_digits")
    # ).group_by("index", "digits", "first_digits").agg(
    #     pl.col("digits").list.slice(pl.col("first_digits").list.arg_max() + 1).list.explode().cum_max().implode().alias("second_digits")
    # ).group_by("index", "digits", "first_digits").agg(
    #     pl.col("digits").list.slice(pl.col("first_digits").list.arg_max() + 1).list.explode().cum_max().implode().alias("second_digits")
    # ).group_by("index", "digits", "first_digits").agg(
    #     pl.col("digits").list.slice(pl.col("first_digits").list.arg_max() + 1).list.explode().cum_max().implode().alias("second_digits")
    # ).group_by("index", "digits", "first_digits").agg(
    #     pl.col("digits").list.slice(pl.col("first_digits").list.arg_max() + 1).list.explode().cum_max().implode().alias("second_digits")
    # ).group_by("index", "digits", "first_digits").agg(
    #     pl.col("digits").list.slice(pl.col("first_digits").list.arg_max() + 1).list.explode().cum_max().implode().alias("second_digits")
    # ).group_by("index", "digits", "first_digits").agg(
    #     pl.col("digits").list.slice(pl.col("first_digits").list.arg_max() + 1).list.explode().cum_max().implode().alias("second_digits")
    # ).group_by("index", "digits", "first_digits").agg(
    #     pl.col("digits").list.slice(pl.col("first_digits").list.arg_max() + 1).list.explode().cum_max().implode().alias("second_digits")
    # ).group_by("index", "digits", "first_digits").agg(
    #     pl.col("digits").list.slice(pl.col("first_digits").list.arg_max() + 1).list.explode().cum_max().implode().alias("second_digits")
    # ).with_columns(
    #     pl.concat_str(
    #         pl.col("first_digits").list.max(),
    #         pl.col("second_digits").list.max(),
    #     ).cast(pl.Int32).alias("joltage")
    # ).sort("index").collect()

    # console.print(df)
    # result = df.select(pl.sum("joltage").cast(pl.String)).item()

    return "0"


def main(submit: bool = False):

    part_functions = [part1, part2]

    day_input = parse_input(get_puzzle_input(YEAR, DAY))
    # print(day_input)

    test_input = parse_input(read_input(Path("test_input.txt")))
    # print(test_input)

    for idx, part in enumerate(part_functions):
        test_result = part(test_input)
        console.print(f"Part {idx+1} Test Result: {test_result}")

        result = part(day_input)
        console.print(f"Part {idx+1} Result: {result}")

        if submit:
            submission_result = submit_puzzle_answer(YEAR, DAY, idx+1, result)
            console.print(submission_result.is_correct, submission_result.message)

if __name__ == "__main__":
    typer.run(main)