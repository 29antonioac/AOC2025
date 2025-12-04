import os
from collections import defaultdict, namedtuple
from enum import Enum
from pathlib import Path

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

YEAR = 2025
DAY = int(Path(__file__).parent.name.split("day")[-1])
LEADERBOARD = os.getenv("BOARD_ID")

console = Console()

class GridElement(str, Enum):
    NOTHING = "."
    ROLL = "@"

Position = namedtuple("Position", ["row", "column"])

class Grid:
    def __init__(self, grid: list[str]):
        self.grid_size: Position
        self.grid: list[list[GridElement]] = []
        self.adjacency_matrix: dict[Position, list[Position]] = defaultdict(list)

        for row, line in enumerate(grid):
            current_row = [
                GridElement(item) for column, item in enumerate(line)
            ]
            self.grid.append(current_row)
        
        self.grid_size = (len(grid), len(grid[0]))

        self._build_adjacency_matrix()

    def __str__(self):
        return "\n".join([
            "".join([
                element
                for element in row])
            for row_idx, row in enumerate(self.grid)
        ])

    def _adjacent_positions(self, position: Position) -> list[Position]:
        return [
            Position(new_row, new_column)
            for i in (-1, 0, 1)
            for j in (-1, 0, 1)
            if 0 <= (new_row := position.row + i) < self.grid_size[0] and 
            0 <= (new_column := position.column + j) < self.grid_size[1] and
            not (i == 0 and j == 0)
        ]
        
    def _build_adjacency_matrix(self) -> None:
        for row_idx, row in enumerate(self.grid):
            for col_idx, element in enumerate(row):
                current_position = Position(row_idx, col_idx)
                if element == GridElement.ROLL:
                    self.adjacency_matrix[current_position] = set(
                        p for p in self._adjacent_positions(current_position)
                    )
    
    def remove_rolls(self) -> int:
        rolls_to_remove: set[Position] = set()
        for position, adjacent in self.adjacency_matrix.items():
            adjacent_rolls = [adjacent_position for adjacent_position in adjacent if self.grid[adjacent_position.row][adjacent_position.column] == GridElement.ROLL]
            if len(adjacent_rolls) < 4:
                rolls_to_remove.add(position)
        
        # Remove rolls once deduped
        for position in rolls_to_remove:
            self.grid[position.row][position.column] = GridElement.NOTHING
            del self.adjacency_matrix[position]
                
        return len(rolls_to_remove)


@timer()
def part1(input_data: list[str]) -> str:
    grid = Grid(input_data)
    # console.print(grid)

    result = grid.remove_rolls()

    return str(result)

@timer()
def part2(input_data: list[str]) -> str:
    grid = Grid(input_data)

    iterations = 0
    removed_rolls = 0
    current_removed_rolls = None
    while current_removed_rolls is None or current_removed_rolls > 0:
        iterations += 1
        current_removed_rolls = grid.remove_rolls()
        removed_rolls = removed_rolls + current_removed_rolls
        console.print(f"Iteration {iterations} - removed {current_removed_rolls} rolls - total {removed_rolls}")
    
    return str(removed_rolls)


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