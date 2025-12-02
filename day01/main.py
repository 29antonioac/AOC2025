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

YEAR = 2025
DAY = int(Path(__file__).parent.name.split("day")[-1])
LEADERBOARD = os.getenv("BOARD_ID")

console = Console()

DIAL_SIZE = 100

@timer()
def part1(input_data: list[str]) -> str:
    df = (
        pl.DataFrame({"line": ["Z50"] + input_data})
        .with_columns(
            pl.col("line").str.slice(0, 1).replace_strict({"R": "1", "L": "-1", "Z": "1"}).cast(pl.Int32).alias("direction"),
            pl.col("line").str.slice(1).cast(pl.Int32).alias("steps"),
        )
        .with_columns(
            (pl.col("steps") * pl.col("direction")).cum_sum().mod(DIAL_SIZE).alias("position")
        )
        .filter(pl.col("position") == 0)
    )

    result = str(df.height)

    return result

@timer()
def part2(input_data: list[str]) -> str:
    df = (
        pl.DataFrame({"line": ["Z50"] + input_data})
        .with_columns(
            pl.col("line").str.slice(0, 1).replace_strict({"R": "1", "L": "-1", "Z": "1"}).cast(pl.Int32).alias("direction"),
            pl.col("line").str.slice(1).cast(pl.Int32).alias("steps"),
        )
        .with_columns(
            pl.col("steps").mod(DIAL_SIZE).alias("steps_normalised"),
            pl.col("steps").floordiv(DIAL_SIZE).alias("steps_carry_over"),
        )
        .with_columns(
            (pl.col("steps_normalised") * pl.col("direction")).cum_sum().mod(DIAL_SIZE).alias("position"),
        )
        .with_columns(
            pl.col("position").shift().alias("prev_position")
        )
        .with_columns(
            (
                ~(pl.col("prev_position") + pl.col("steps_normalised") * pl.col("direction")).is_between(pl.lit(0), pl.lit(DIAL_SIZE - 1))
                & (pl.col("position") != 0) & (pl.col("prev_position") != 0)
            ).alias("crossed_but_not_zero")
        )
    )

    df_result = df.select(
        pl.sum_horizontal(
            pl.col("steps_carry_over").sum(),
            (pl.col("position") == 0).sum(),
            pl.col("crossed_but_not_zero").cast(pl.Int32).sum(),
        ).alias("result")
    )

    console.print(df)
    console.print(df_result)

    result = str(df_result.item())

    return result


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