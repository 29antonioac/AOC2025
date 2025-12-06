import os
import re
from functools import reduce
from io import StringIO
from math import log10
from pathlib import Path

import polars as pl
import polars.selectors as cs
import typer
from elf import (
    get_puzzle_input,
    submit_puzzle_answer,
    get_private_leaderboard,
    get_user_status,
    OutputFormat,
)
from elf.helpers import timer
from rich.console import Console

pl.Config.set_tbl_rows(20)
pl.Config.set_tbl_cols(20)
pl.Config.set_fmt_str_lengths(200)
pl.Config.set_fmt_table_cell_list_len(20)

YEAR = 2025
DAY = int(Path(__file__).parent.name.split("day")[-1])
LEADERBOARD = os.getenv("BOARD_ID")

console = Console()

def read_input(path: Path) -> str:
    """Read input from a file and return its contents."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Input file not found: {path}. Please add the missing file."
        )
    return path.read_text(encoding="utf-8")

def parse_input_part1(input_data: str) -> list[str]:
    return [l_clean for l in re.sub(" +", " ", input_data.strip()).split("\n") if (l_clean := l.strip())]

def parse_input_part2(input_data: str) -> list[str]:
    return [l_clean for l in input_data.replace(" ", "0").split("\n") if (l_clean := l.strip())]


@timer()
def part1(input_data: list[str]) -> str:
    n_columns = len(input_data[0])
    to_read = "\n".join(input_data[:-1])
    operations = input_data[-1].split(" ")
    # console.print(operations)
    # console.print(to_read)
    df = (
        pl.scan_csv(
            StringIO(to_read), 
            separator=" ",
            has_header=False,
        )
        .select(
            pl.sum_horizontal([
                pl.col(f"column_{i+1}").product() 
                if op == "*" 
                else pl.sum(f"column_{i+1}")
                for i, op in enumerate(operations)
            ])
        )
        .collect()
    )

    # console.print(df)
    
    result = df.item()
    return str(result)

@timer()
def part2(input_data: list[str]) -> str:
    n_columns = len(input_data)
    numeric_cols = [f"column_{i}" for i in range(n_columns-1)]
    # console.print(numeric_cols)
    to_read = [list(l) for l in input_data]
    operations = input_data[-1].split(" ")
    # console.print(operations)
    # console.print(to_read)
    df = (
        pl.DataFrame(
            to_read, 
            orient="col",
        )
        .with_columns(pl.all().replace(0, None))
        .rename({f"column_{n_columns-1}": "operation"})
        .with_columns(
            pl.when(pl.all_horizontal(cs.starts_with("column_").is_null())).then(pl.lit("---")).otherwise(pl.col("operation")).alias("operation")
        )
    )

    # console.print(df)

    df_result = (
        df
        .with_columns(
           pl.col("operation").fill_null(strategy="forward")
        )
        .select(
            pl.concat_str(cs.starts_with("column_"), ignore_nulls=True).cast(pl.UInt64, strict=False).alias("n"),
            "operation",
            pl.col("operation").rle_id().alias("rle_id")
        )
        .filter(
            pl.col("n").is_not_null()
        )
        .group_by(
            "rle_id",
            "operation",
        )
        .agg(
            pl.col("n").filter(pl.col("operation") == "*").product().alias("product"),
            pl.col("n").filter(pl.col("operation") == "+").sum().alias("sum"),
        )
        .select(
            pl.when(pl.col("operation") == "*").then(pl.col("product")).otherwise(pl.col("sum")).sum().cast(pl.String).alias("sum")
        )
    )

    # console.print(df_result)
    
    result = df_result.item()
    return str(result)



def main(submit: bool = False):

    part_functions = [part1, part2]
    parse_functions = [parse_input_part1, parse_input_part2]

    for idx, part in enumerate(part_functions):
        day_input = parse_functions[idx](get_puzzle_input(YEAR, DAY))
        # print(day_input)

        test_input = parse_functions[idx](read_input(Path("test_input.txt")))
        # print(test_input)

    
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