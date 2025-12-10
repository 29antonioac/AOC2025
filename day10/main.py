import os
import re
from collections import deque
from functools import cache, reduce
from io import StringIO
from itertools import combinations
from math import log10
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
from elf.helpers import timer
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, PULP_CBC_CMD, value
from rich.console import Console

YEAR = 2025
DAY = 10
LEADERBOARD = os.getenv("BOARD_ID")

console = Console()

class Machine:
    def __init__(self, input_line: str):

        raw_state, raw_rest = input_line.split("] ")
        raw_buttons, raw_joltage = raw_rest.split(" {")

        self.initial_state = np.zeros(len(raw_state.replace("[", "")))
        self.lights = np.array([s == "#" for s in raw_state.replace("[", "")]).astype(int)

        buttons = []
        for button in raw_buttons.strip().split(" "):
            arr = np.zeros(len(self.initial_state))
            positions = list(map(int, button.strip("()").split(",")))
            arr[positions] = True
            buttons.append(arr)
        self.buttons = np.array(buttons)

        self.joltage = list(map(int, raw_joltage.strip("{}").split(",")))

    def __str__(self):
        goal_state = f"State: {self.lights}"
        buttons = f"Buttons: {self.buttons}"
        joltage = f"Joltage: {self.joltage}"

        return "\n\n".join([goal_state, buttons, joltage])
    def __repr__(self):
        return str(self)
    
    def turn_on(self, light_or_joltage: str):
        # Implement BFS where the root is the initial state and the leaves are 
        # (True, True, ...)
        # The state change are the buttons array
        explored = np.array([self.initial_state])

        # console.print(f"Turning on {light_or_joltage}...")
        goal_state = self.lights if light_or_joltage == "light" else self.joltage

        depth = 0
        curr_w = [self.initial_state]

        while curr_w:
            q = curr_w
            curr_w = []
            for v in q:
                # console.print(f"Q = {q}")
                # console.print(f"V = {v}")
                
                # console.print("Exploring buttons...")
                for b in self.buttons:
                    
                    # console.print(f"Q = {q}")
                    if light_or_joltage == "light":
                        w = (v + b) % 2
                    else:
                        # console.print(f"V = {v}, B = {b}")
                        # console.print(f"V + B = {v + b}")
                        w = v + b
                        # console.print(f"W = {w}")
                        # console.print(f"Goal State = {goal_state}")
                    # console.print(f"B = {b}")
                    # console.print(f"Checking new state: {w}")
                    if (w == goal_state).all():
                        return depth + 1
                    if (w == explored).all(axis=1).any() and light_or_joltage == "light":
                        # console.print(f"{w} already explored, {light_or_joltage} skipping")
                        continue
                    if (w > goal_state).any() and light_or_joltage == "joltage":
                        # console.print(f"{w} exceeds goal state {goal_state}, skipping")
                        continue
                    explored = np.vstack([explored, w])                    
                    curr_w.append(w)
            # console.print(f"Depth {depth} completed, new wavefront size: {len(curr_w)}")
            depth += 1

        raise ValueError("Goal state not reachable")
            


def read_input(path: Path) -> str:
    """Read input from a file and return its contents."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Input file not found: {path}. Please add the missing file."
        )
    return path.read_text(encoding="utf-8")

def parse_input(input_data: str) -> list[Machine]:
    return [Machine(line) for line in input_data.split("\n") if line]


@timer()
def part1(input_data: str) -> str:
    machines = parse_input(input_data)

    solution = 0
    for idx, machine in enumerate(machines):
        # console.print(f"Machine {idx}")
        # console.print(machine)
        min_steps = machine.turn_on("light")
        solution += min_steps
        # console.print(f"Min steps to turn on: {min_steps}")
        # console.print()
    
    result = str(solution)
    return result
@timer()
def part2(input_data: str) -> str:
    
    machines = parse_input(input_data)

    solution = 0
    for machine in machines:
        A = machine.buttons.transpose()
        C = machine.joltage

        # Problem: minimize sum of the number of button presses to reach the joltage C
        # Ax = C
        # A is the button matrix (each column is a button, needs transpose)
        # x is the number of times each button is pressed (integer variables)
        # C is the target joltage vector
        prob = LpProblem("MinSum", LpMinimize)

        # Variables: number of times each button is pressed
        # Each one is a non-negative integer (we cannot unpress a button)
        # Each column in A corresponds to a variable in x (each button)
        x = [
            LpVariable(f"x{i}", lowBound=0, cat="Integer") 
            for i in range(len(A[0]))
        ]

        # Objective: minimise the sum of button presses
        # minimise x[0] + x[1] + ... + x[n]
        prob += lpSum(x)

        # Constraints: Ax = C
        # Each button press combination must match to the target joltage C
        for i in range(len(A)):
            prob += lpSum(A[i][j] * x[j] for j in range(len(A[0]))) == C[i]

        # PULP_CBC_CMD seems to be the default solver
        # Setting msg=0 to suppress output
        prob.solve(PULP_CBC_CMD(msg=0))
        solution += int(value(prob.objective))
    
    result = str(solution)
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