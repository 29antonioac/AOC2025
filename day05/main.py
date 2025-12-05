import os
from functools import reduce
from math import log10
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
from elf.helpers import read_input, timer
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

def parse_input(input_data: str) -> tuple[list[str], list[str]]:
    fresh_ingredients, _, available_ingredients = input_data.partition("\n\n")

    fresh_ingredients = fresh_ingredients.split("\n")
    available_ingredients = available_ingredients.split("\n")

    return fresh_ingredients, available_ingredients

@timer()
def part1(input_data: tuple[list[str], list[str]]) -> str:
    fresh_ingredients, available_ingredients = input_data

    df_fresh = (
        pl.DataFrame({"id": fresh_ingredients}).lazy()
        .select(
            pl.col("id").str.split("-").cast(pl.List(pl.Int64)).alias("id_range")
        )
    )

    console.print(df_fresh)
    console.print(available_ingredients)

    df_available = (
        pl.DataFrame({"id": available_ingredients}).lazy()
        .filter(pl.col("id") != "")
        .select(
            pl.col("id").cast(pl.Int64)
        )
    )

    console.print(df_available)

    df_available_fresh = (
        df_available
        .join_where(
            df_fresh,
            pl.col("id") >= pl.col("id_range").list.get(0),
            pl.col("id") <= pl.col("id_range").list.get(1),
        )
        .collect()
    )
    console.print(df_available_fresh)

    result = df_available_fresh.select(pl.col("id").unique().len().cast(pl.String)).item()

    return result

@timer()
def part2(input_data: tuple[list[str], list[str]]) -> str:
    fresh_ingredients, available_ingredients = input_data

    sorted_ingredients = sorted(
        [i for i in fresh_ingredients if i], key=lambda x: int(x.partition("-")[0])
    )

    # console.print(sorted_ingredients)

    all_ranges = []
    all_sum = 0
    for r in sorted_ingredients:
        lower_bound, _, upper_bound = r.partition("-")
        
        lower_bound = int(lower_bound)
        upper_bound = int(upper_bound)
        # If there's no overlap, add a new range
        if not all_ranges or all_ranges[-1][1] < lower_bound:
            all_ranges.append((lower_bound, upper_bound))
        # If there is overlap, enlarge latest range just with the new portion of range
        else:
            lower_bound = all_ranges[-1][0]
            upper_bound = max(all_ranges[-1][1], upper_bound)
            all_ranges[-1] = (lower_bound, upper_bound)

    console.print(all_ranges)

    result = sum((
        r[-1] - r[0] + 1
        for r in all_ranges
    ))

    return result


def main(submit: bool = False):

    part_functions = [part1, part2]

    day_input = parse_input(get_puzzle_input(YEAR, DAY))
    # print(day_input)

    test_input = parse_input(read_input(Path("test_input.txt")))
    # print(test_input)

    for idx, part in enumerate(part_functions):
        test_result = part(test_input)
        console.print(f"Part {idx+1} Test Result: {test_result}")

        result = part(day_input)
        console.print(f"Part {idx+1} Result: {result}")

        if submit:
            if result == "0":
                console.print(f"Part {idx+1} has not been tried to resolve, skipping...")
                continue
            submission_result = submit_puzzle_answer(YEAR, DAY, idx+1, result)
            console.print(submission_result.is_correct, submission_result.message)

if __name__ == "__main__":
    typer.run(main)