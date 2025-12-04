import os
from collections import defaultdict, namedtuple
from enum import Enum
from pathlib import Path

import numpy as np
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
from scipy.signal import convolve2d

YEAR = 2025
DAY = int(Path(__file__).parent.name.split("day")[-1])
LEADERBOARD = os.getenv("BOARD_ID")

console = Console()


def get_rolls_to_remove(grid: np.ndarray) -> np.ndarray:
    kernel = np.array([
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
    ])

    convolution_result = convolve2d(grid, kernel, mode='same', boundary='fill', fillvalue=0)
    convoluted_filtered = grid * convolution_result

    rolls_to_remove = (grid == 1) & (convoluted_filtered < 4)

    return rolls_to_remove


@timer()
def part1(input_data: list[str]) -> str:
    grid = np.array(
        [list(line) for line in input_data],
    )
    grid_parse = np.where(grid == "@", 1, 0)
    console.print(grid_parse)

    rolls_to_remove = get_rolls_to_remove(grid_parse)
    console.print(rolls_to_remove)

    result = np.sum(rolls_to_remove)

    return str(result)

@timer()
def part2(input_data: list[str]) -> str:
    grid = np.array(
        [list(line) for line in input_data],
    )
    grid_parse = np.where(grid == "@", 1, 0)
    console.print(grid_parse)

    total_removed = 0
    current_removed = 0
    
    while total_removed == 0 or current_removed > 0:
        rolls_to_remove = get_rolls_to_remove(grid_parse)
        current_removed = np.sum(rolls_to_remove)
        if current_removed > 0:
            total_removed += current_removed
            console.print(f"Current removed: {current_removed} - Total removed so far: {total_removed}")
            grid_parse = grid_parse * (~rolls_to_remove)
    
    result = total_removed

    return str(result)

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
            if result == "0":
                console.print(f"Part {idx+1} has not been tried to resolve, skipping...")
                continue
            submission_result = submit_puzzle_answer(YEAR, DAY, idx+1, result)
            console.print(submission_result.is_correct, submission_result.message)

if __name__ == "__main__":
    typer.run(main)