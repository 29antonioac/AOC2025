import os
import re
from functools import cache, reduce
from io import StringIO
from itertools import combinations
from math import log10
from pathlib import Path

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
from rich.progress import track

YEAR = 2025
DAY = 9
LEADERBOARD = os.getenv("BOARD_ID")

console = Console()


def read_input(path: Path) -> str:
    """Read input from a file and return its contents."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Input file not found: {path}. Please add the missing file."
        )
    return path.read_text(encoding="utf-8")


class Point:
    def __init__(self, coordinates: str):
        self.x, self.y = map(int, coordinates.split(","))

    def __str__(self) -> str:
        return f"{self.x},{self.y}"

    def __repr__(self) -> str:
        return f"{self.x},{self.y}"

    def __lt__(self, another) -> bool:
        return str(self) < str(another)

    def __le__(self, another) -> bool:
        return str(self) <= str(another)
    
    def __hash__(self):
        return hash(self.x) + hash(self.y)


class Rectangle:
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2
        self.area = (abs(p1.x - p2.x) + 1) * (abs(p1.y - p2.y) + 1)
        self.min_x = min(p1.x, p2.x)
        self.max_x = max(p1.x, p2.x)
        self.min_y = min(p1.y, p2.y)
        self.max_y = max(p1.y, p2.y)

    def __str__(self):
        return f"{self.p1} <-> {self.p2} : {self.area:.2f}"

    def __repr__(self):
        return f"{self.p1} <-> {self.p2} : {self.area:.2f}"

    def __hash__(self):
        return hash((self.p1, self.p2) if self.p1 < self.p2 else (self.p2, self.p1))

    def points(self):
        for x in range(self.min_x, self.max_x + 1):
            for y in range(self.min_y, self.max_y + 1):
                yield Point(f"{x},{y}")


def contains_not_border(r: Rectangle, p: "Point") -> bool:
    return (r.min_x < p.x < r.max_x) and (
        r.min_y < p.y < r.max_y
    )


@timer()
def part1(input_data: str) -> str:
    points = [Point(l) for l in input_data.strip().split("\n")]

    rectangles = sorted(
        [Rectangle(p1, p2) for p1, p2 in combinations(points, 2)], key=lambda e: e.area
    )

    # console.print(rectangles)
    result = rectangles[-1].area
    return str(result)


@timer()
def part2(input_data: str) -> str:
    reds = [Point(l) for l in input_data.strip().split("\n")]

    greens = {
        p for idx in range(len(reds)) for p in Rectangle(reds[idx], reds[(idx + 1) % len(reds)]).points()
    }

    rectangles = sorted(
        [Rectangle(p1, p2) for p1, p2 in combinations(reds, 2)],
        key=lambda e: e.area,
        reverse=True,
    )
    console.print(f"All rectangles computed {len(rectangles)}")

    r: Rectangle
    for r in track(rectangles):
        if not any(contains_not_border(r, g) for g in greens):
            break

    result = r.area
    return str(result)


def main(submit: bool = False):
    part_functions = [part1, part2]

    for idx, part in enumerate(part_functions):
        day_input = get_puzzle_input(YEAR, DAY)
        # print(day_input)

        test_input = read_input(Path("test_input.txt"))
        # print(test_input)

        test_result = part(test_input)
        console.print(f"Part {idx + 1} Test Result: {test_result}")

        result = part(day_input)
        console.print(f"Part {idx + 1} Result: {result}")

        if submit:
            if result == "0":
                console.print(
                    f"Part {idx + 1} has not been tried to resolve, skipping..."
                )
                continue
            submission_result = submit_puzzle_answer(YEAR, DAY, idx + 1, result)
            console.print(submission_result.is_correct, submission_result.message)


if __name__ == "__main__":
    typer.run(main)
