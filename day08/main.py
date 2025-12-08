import os
import re
from functools import cache, reduce
from io import StringIO
from itertools import combinations
from math import log10
from pathlib import Path

import polars as pl
import polars_ds as pds
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

# def parse_input_part1(input_data: str) -> list[str]:
#     return [l_clean for l in re.sub(" +", " ", input_data.strip()).split("\n") if (l_clean := l.strip())]

# def parse_input_part2(input_data: str) -> list[str]:
#     return [l_clean for l in input_data.replace(" ", "0").split("\n") if (l_clean := l.strip())]


# @timer()
# def part1(input_data: str) -> str:
#     df = pl.read_csv(
#         StringIO(input_data),
#         has_header=False,
#     )

#     # console.print(df)

#     df_1nn = (
#         df
#         .with_row_index()
#         .with_columns(
#             pds.query_knn_ptwise(
#                 pl.col("column_1"),
#                 pl.col("column_2"),
#                 pl.col("column_3"),
#                 index="index",
#                 k=1,
#                 dist="sql2",
#                 parallel=True,
#                 max_bound=999999999,
#                 return_dist=True,
#             ).alias("neighbours")
#         )
#         .with_columns(
#             pl.col("neighbours").struct.field("idx").list.get(-1).alias("closest"),
#             pl.col("neighbours").struct.field("dist").list.get(-1).alias("distance")
#         )
#         .sort("distance")
#     )

#     if df_1nn.select(
#         pl.col("neighbours").struct.field("idx").list.len().min()
#     ).item() == 1:
#         raise ValueError("Some point is missing a neighbour within max_bound")

#     console.print(df_1nn)
    
#     result = "0"
#     return str(result)

class Point:
    def __init__(self, coordinates: str):
        self.x, self.y, self.z = map(int, coordinates.split(","))

    def __str__(self) -> str:
        return f"{self.x},{self.y},{self.z}"
    
    def __repr__(self) -> str:
        return f"{self.x},{self.y},{self.z}"

    def __lt__(self, another) -> bool:
        return str(self) < str(another)
    
    def __le__(self, another) -> bool:
        return str(self) <= str(another)

class Edge:
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2
        self.weight = ((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)**(1/2)

    def __str__(self):
        return f"{self.p1} <-> {self.p2} : {self.weight:.2f}"
    
    def __repr__(self):
        return f"{self.p1} <-> {self.p2} : {self.weight:.2f}"

def find_sets(p: Point, sets: list[set[Point]]):
    for idx, s in enumerate(sets):
        if p in s:
            return idx
    
    raise ValueError(f"Point {p} not found in any set")



@timer()
def part1(input_data: str) -> str:
    points = [Point(l) for l in input_data.strip().split("\n")]
    edges = sorted([Edge(p1, p2) for p1, p2 in combinations(points, 2)], key=lambda e: e.weight)

    circuits = [set([p]) for p in points]
    forest = set()

    for edge in edges[:1000]:
        # console.print(f"Processing edge: {edge}")
        if (idx1 := find_sets(edge.p1, circuits)) != (idx2 := find_sets(edge.p2, circuits)):
            # console.print(f"Accepting edge {edge}")
            forest.add(edge)
            new_circuit = circuits[idx1] | circuits[idx2]
            if idx2 < idx1:
                del circuits[idx1]
                del circuits[idx2]
            else:
                del circuits[idx2]
                del circuits[idx1]
            circuits.append(new_circuit)
            # console.print(f"New circuit {new_circuit}")
            # console.print(f"Circuits now: {circuits}")
    
    sorted_circuits = sorted(circuits, key=lambda s: len(s), reverse=True)
    
    console.print(sorted_circuits[:3])

    # console.print(forest)

    result = reduce(lambda x, y: x * y, [len(s) for s in sorted_circuits[:3]])
    
    # result = "0"
    return str(result)

@timer()
def part2(input_data: str) -> str:
    points = [Point(l) for l in input_data.strip().split("\n")]
    edges = sorted([Edge(p1, p2) for p1, p2 in combinations(points, 2)], key=lambda e: e.weight)

    circuits = [set([p]) for p in points]
    forest = set()

    for edge in edges:
        if len(circuits) == 1:
            break
        # console.print(f"Processing edge: {edge}")
        if (idx1 := find_sets(edge.p1, circuits)) != (idx2 := find_sets(edge.p2, circuits)):
            # console.print(f"Accepting edge {edge}")
            forest.add(edge)
            new_circuit = circuits[idx1] | circuits[idx2]
            if idx2 < idx1:
                del circuits[idx1]
                del circuits[idx2]
            else:
                del circuits[idx2]
                del circuits[idx1]
            circuits.append(new_circuit)
            last_connection_product_x = edge.p1.x * edge.p2.x
            # console.print(f"New circuit {new_circuit}")
            # console.print(f"Circuits now: {circuits}")

    # console.print(forest)

    result = str(last_connection_product_x)
    
    # result = "0"
    return str(result)



def main(submit: bool = False):

    part_functions = [part1, part2]

    for idx, part in enumerate(part_functions):
        day_input = get_puzzle_input(YEAR, DAY)
        # print(day_input)

        test_input = read_input(Path("test_input.txt"))
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