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

def parse_input(input_data: str) -> list[str]:
    return [list(l) for l in input_data.split("\n") if l]

@timer()
def part1(input_data: list[str]) -> str:
    col_start = input_data[0].index("S")

    splits = 0

    for idx, line in enumerate(input_data):
        if idx == 0:
            # First iteration just get the first beam below star (input is clean)
            beams_to_check = set([(1, col_start)])
        else:
            # Each iteration check if the current line splits (and do it)
            new_beams = set()
            for beam in beams_to_check:
                # console.print(beam)
                row_to_check = beam[0]
                col_to_check = beam[1]
                if input_data[row_to_check][col_to_check] == ".":
                    new_beams.add((row_to_check + 1, col_to_check))
                elif input_data[row_to_check][col_to_check] == "^":
                    # We need to split but looking after col boundaries
                    # Only consider the split if within the boundaries
                    if col_to_check - 1 >= 0:
                        new_beams.add((row_to_check + 1, col_to_check - 1))
                    if col_to_check + 1 < len(input_data[0]):
                        new_beams.add((row_to_check + 1, col_to_check + 1))
                    splits += 1
                else:
                    raise ValueError(f"Unexpected character {input_data[row_to_check][col_to_check]} at {(row_to_check, col_to_check)}")
            
            # Get beams as new_beams for the next line's check
            beams_to_check = new_beams

        # console.print(f"{idx}: {line}")

    return str(splits)

@timer()
def part2(input_data: list[str]) -> str:
    col_start = input_data[0].index("S")

    paths = []

    for idx, line in enumerate(input_data):
        if idx == 0:
            # First iteration just get the first path, starting below star (input is clean)
            paths.append([(1, col_start)])
        else:
            # Each iteration check for each path if the next line splits (and do it)
            new_paths = []
            console.print(f"Processing line {idx} with {len(paths)} paths")
            # console.print(paths)
            for path in paths:
                # console.print(path)
                row_to_check = path[-1][0]
                col_to_check = path[-1][1]
                if input_data[row_to_check][col_to_check] == ".":
                    # If not splitting, update current path
                    path.append((row_to_check + 1, col_to_check))
                elif input_data[row_to_check][col_to_check] == "^":
                    # If splitting, we need to update this path and create a new one
                    # We need to split but looking after col boundaries
                    # Only consider the split if within the boundaries
                    # Splitting on the left creates a new path
                    # Current path updates when splitting on the right
                    if col_to_check - 1 >= 0:
                        new_paths.append(path + [(row_to_check + 1, col_to_check - 1)])
                    if col_to_check + 1 < len(input_data[0]):
                        path.append((row_to_check + 1, col_to_check + 1))
                else:
                    raise ValueError(f"Unexpected character {input_data[row_to_check][col_to_check]} at {(row_to_check, col_to_check)}")
            
            # Get beams as new_beams for the next line's check
            if new_paths:
                paths.extend(new_paths)

        # console.print(f"{idx}: {line}")

    return str(len(paths))

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