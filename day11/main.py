import os
from collections import defaultdict, deque
from pathlib import Path

import typer
from elf import (
    get_puzzle_input,
    submit_puzzle_answer,
)
from elf.helpers import timer
from rich.console import Console

YEAR = 2025
DAY = 11
LEADERBOARD = os.getenv("BOARD_ID")

console = Console()
DEPTH_BUFFER = int(os.environ.get("DEPTH_BUFFER", 0))
MAX_DEPTH = int(os.environ.get("MAX_DEPTH", 17))

class Node:
    def __init__(self, label: str, parents: int = 0):
        self.label = label
        self.parents: int = parents

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
            destination_nodes = destination_labels.split(" ")
            self.nodes[source_label] = destination_nodes

    def find_all_paths(
        self, initial_state_label: str = "you", final_state_label: str = "out"
    ):
        # Implement BFS with path counting
        paths_to = defaultdict(int)
        paths_to[(initial_state_label, 0)] = 1
        explored = set()

        q: deque[Node] = deque()
        initial_state = Node(initial_state_label)
        q.append(initial_state)

        while len(q) > 0:
            v = q.popleft()
            if (v.label, v.parents) in explored:
                continue
            explored.add((v.label, v.parents))
            
            if (v.label not in self.nodes):
                continue
            
            # console.print(f"Exploring depth {v.parents}")
            for dest_label in self.nodes[v.label]:
                paths_to[(dest_label, v.parents + 1)] += paths_to[(v.label, v.parents)]
                if (dest_label, v.parents + 1) not in explored:
                    q.append(Node(dest_label, v.parents + 1))
        # Sum all paths that reached the final state at any depth
        total_paths = sum(count for (label, depth), count in paths_to.items() if label == final_state_label)
        console.print(
            f"Found {total_paths} solutions from {initial_state_label} to {final_state_label}"
        )
        return total_paths


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

    result_svr_fft = graph.find_all_paths("svr", "fft")
    result_fft_dac = graph.find_all_paths("fft", "dac")
    result_dac_out = graph.find_all_paths("dac", "out")

    result = str(
        (
            result_svr_fft * result_fft_dac * result_dac_out
        )
    )

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
