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

def parse_input(input_data: str) -> list[str]:
    return [r.strip() for r in input_data.split(",")]

@timer()
def part1(input_data: list[str]) -> str:
    df = pl.DataFrame(
        {"range": input_data}
    ).select(
        pl.col("range").str.split("-").list.eval(pl.element().cast(pl.Int64))
    ).with_columns(
        pl.int_ranges(
            pl.col("range").list.get(0), pl.col("range").list.get(-1) + 1     
        ).list.filter(pl.element().log10().cast(pl.Int32) % 2 != 0).cast(pl.List(pl.String)).alias("potential_bad_ids")
    ).with_columns(
        pl.col("potential_bad_ids").list.filter(
            pl.element().str.slice(0, pl.element().str.len_chars() / 2) == pl.element().str.slice(pl.element().str.len_chars() / 2)
        ).cast(pl.List(pl.Int64)).alias("bad_ids")
    ).with_columns(
        pl.col("bad_ids").list.sum().alias("sum_bad_ids")
    )

    console.print(df)
    result = df.select(pl.sum("sum_bad_ids").cast(pl.String)).item()

    return result

@timer()
def part2(input_data: list[str]) -> str:
    

    df = pl.DataFrame(
        {"range": input_data}
    ).select(
        pl.col("range").str.split("-").list.eval(pl.element().cast(pl.Int64))
    )

    max_id = df.select(
        pl.col("range").list.get(-1)
    ).max().item()

    max_splits = int(log10(max_id) // 2 + 1)

    console.print(f"Max ID: {max_id}")
    console.print(f"Max number of splits: {max_splits}")

    or_expr = reduce(
        lambda x, y: x | y,
        [
            pl.element().str.slice(0, pl.element().str.len_chars() / i).repeat_by(pl.lit(i)).list.join("") == pl.element()
            for i in range(2, max_splits + 1)
        ] + [pl.element().str.slice(0, 1).repeat_by(pl.element().str.len_chars()).list.join("") == pl.element()]
    )
    
    df_all_bad_ids = df.lazy().with_columns(
        pl.int_ranges(
            pl.col("range").list.get(0), pl.col("range").list.get(-1) + 1     
        ).cast(pl.List(pl.String)).list.filter(pl.element().str.len_chars() > 1).alias("potential_bad_ids")
    ).with_columns(
        pl.col("potential_bad_ids").list.filter(
            or_expr
        ).cast(pl.List(pl.Int64)).alias("bad_ids")
    ).collect()

    console.print(df_all_bad_ids.drop("potential_bad_ids"))
    df_result = df_all_bad_ids.group_by(pl.lit(1)).agg(
        pl.concat_list("bad_ids").flatten()
    ).with_columns(pl.col("bad_ids").list.unique().list.sum().alias("sum_bad_ids"))
    console.print(df_result)
    result = df_result.select(pl.sum("sum_bad_ids").cast(pl.String)).item()

    return result


def main(submit: bool = False):

    part_functions = [part1, part2]

    day_input = parse_input(get_puzzle_input(YEAR, DAY))
    print(day_input)

    test_input = parse_input(read_input(Path("test_input.txt")))
    print(test_input)

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