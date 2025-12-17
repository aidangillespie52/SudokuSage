from __future__ import annotations

from dataclasses import dataclass, asdict
from time import perf_counter
from typing import Optional
from pathlib import Path
import csv
import asyncio
import time

from backend.utils import get_logger
from backend.services.board import solve_board, generate_board
from backend.services.ai import call_llm, build_messages, add_board_to_dict_messages
from backend.config.hints import SINGLE_HINT
from backend.services.hints import extract_hint_fields
from sudokusage_eval.metrics.validity import is_valid_solution

logger = get_logger(__name__)
logger.setLevel("INFO")


@dataclass
class SampleRow:
    batch_id: float
    sample_idx: int
    model_name: str
    difficulty: float
    include_solved: bool
    latency_sec: float
    correct: bool
    hint_r: int
    hint_c: int
    hint_value: int
    problem_board: str
    solved_board: str


def _write_csv(path: Path, rows: list[SampleRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists() and path.stat().st_size > 0

    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(asdict(rows[0]).keys()),
        )

        if not file_exists:
            writer.writeheader()

        for r in rows:
            writer.writerow(asdict(r))



def run_sample(
    *,
    model_name: str,
    difficulty: float,
    samples: int,
    include_solved: bool = False,
    out: Optional[str | Path] = None,
) -> None:
    rows: list[SampleRow] = []

    id = time.time()

    total_latency = 0.0
    total_correct = 0
    seen_boards = set()

    for i in range(samples):
        # create board
        pzl_str = generate_board(difficulty=difficulty)
        while pzl_str in seen_boards:
            pzl_str = generate_board(difficulty=difficulty)

        seen_boards.add(pzl_str)

        pzl_str = generate_board(difficulty=difficulty)
        solved = solve_board(pzl_str)

        msgs = build_messages(SINGLE_HINT)
        msgs = add_board_to_dict_messages(
            msgs,
            board=pzl_str,
            solution=solved,
            include_solved=include_solved,
        )

        # call llm
        start = perf_counter()
        response = asyncio.run(call_llm(msgs, model=model_name))
        latency = perf_counter() - start

        # parse results
        hint = extract_hint_fields(response)
        hint_str_pos = (hint.r - 1) * 9 + (hint.c - 1)
        predicted_board = (
            pzl_str[:hint_str_pos] + str(hint.value) + pzl_str[hint_str_pos + 1 :]
        )

        correct = is_valid_solution(predicted_board, solved)

        total_latency += latency
        total_correct += int(correct)

        rows.append(
            SampleRow(
                batch_id=id,
                sample_idx=i + 1,
                model_name=model_name,
                difficulty=difficulty,
                include_solved=include_solved,
                latency_sec=latency,
                correct=correct,
                hint_r=hint.r,
                hint_c=hint.c,
                hint_value=hint.value,
                problem_board=pzl_str,
                solved_board=solved,
            )
        )

    # write csv
    if out and rows:
        _write_csv(Path(out), rows)

    # print averages
    mean_latency = total_latency / samples if samples else 0.0
    accuracy = total_correct / samples if samples else 0.0

    logger.info(
        f"Avg latency: {mean_latency:.6f}s | Accuracy: {accuracy:.3%} "
        f"({total_correct}/{samples})"
    )
    if out:
        logger.info(f"Wrote CSV: {out}")
