import os
import re
from collections import defaultdict, deque
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

YEAR = 2025
DAY = 11
LEADERBOARD = os.getenv("BOARD_ID")

console = Console()

class Node:
    def __init__(self, label: str, parents: tuple[str, ...] | None = None):
        self.label = label
        self.parents: tuple[str, ...] = parents or ()

    def __str__(self):
        return f"Node({self.label})"
    
    def __repr__(self):
        return str(self)

    

class Graph:
    def __init__(self, input_lines: list[str]):

        self.nodes: dict[str, list[str]] = {}
        for line in input_lines:
            # console.print(f"Processing line {line}")
            if not line.strip():
                continue
            (source_label, destination_labels) = line.split(": ")
            destination_nodes = [l for l in destination_labels.split(" ")]
            self.nodes[source_label] = destination_nodes



    # def __str__(self):
    #     goal_state = f"State: {self.lights}"
    #     buttons = f"Buttons: {self.buttons}"
    #     joltage = f"Joltage: {self.joltage}"

    #     return "\n\n".join([goal_state, buttons, joltage])
    # def __repr__(self):
    #     return str(self)
    
    def find_all_paths(self, initial_state_label: str = "you", final_state_label: str = "out"):
        # Implement DFS 
        explored: set[Node] = set()
        solutions: set[Node] = set()
        solutions_from_node: dict[str, int] = defaultdict(int)

        q: deque[Node] = deque()
        initial_state = Node(initial_state_label, None)
        q.append(initial_state)
        explored.add(initial_state_label)

        while len(q) > 0:
            v = q.pop()
            if v.label == final_state_label:
                solutions.add(v)
                for parent in v.parents:
                    solutions_from_node[parent] += 1
            elif v.label not in self.nodes:
                continue
            else:
                explored.add(v.label)
                for dest_label in self.nodes[v.label]:
                    new_node = Node(dest_label, v.parents + (v.label,))
                    if new_node not in explored:
                        q.append(new_node)

        return solutions_from_node[initial_state_label]


def read_input(path: Path) -> str:
    """Read input from a file and return its contents."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Input file not found: {path}. Please add the missing file."
        )
    return path.read_text(encoding="utf-8")

def parse_input(input_data: str) -> Graph:
    return Graph(input_data.split("\n"))


@timer()
def part1(input_data: str) -> str:
    graph = parse_input(input_data)

    result = str(graph.find_all_paths("you", "out"))
    
    return result
@timer()
def part2(input_data: str) -> str:
    
    graph = parse_input(input_data)

    result = str(graph.find_all_paths("svr", "fft"))
    
    return result



def main(submit: bool = False):

    part_functions = [part1, part2]

    for idx, part in enumerate(part_functions):
        # if idx == 1:
        #     break
        day_input = get_puzzle_input(YEAR, DAY)
        # print(day_input)

        test_input = read_input(Path("test_input.txt"))
        # print(test_input)

        if idx + 1 == 1:
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