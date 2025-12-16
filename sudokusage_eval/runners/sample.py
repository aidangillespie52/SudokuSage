from dataclasses import dataclass
from time import perf_counter
from typing import Dict, Any, Optional
from backend.utils import get_logger

import asyncio

from backend.services.board import solve_board, generate_board, puzzle_to_str
from backend.services.ai import call_llm, build_messages, add_board_to_dict_messages
from backend.config.hints import SINGLE_HINT
from backend.services.hints import extract_hint_fields

from sudokusage_eval.metrics.validity import is_valid_solution

logger = get_logger(__name__)
logger.setLevel("INFO")

BOARD_SIZE = 81

def run_sample(
    *,
    model_name: str,
    difficulty: float,
    samples: int,
    include_solved: bool = True) -> None:

    for i in range(samples):
        logger.info(f"Running sample {i+1}/{samples}...")

        # create board
        pzl_str = generate_board(difficulty=difficulty)
        solved = solve_board(pzl_str)
        
        msgs = build_messages(SINGLE_HINT)
        msgs = add_board_to_dict_messages(
            msgs,
            board=pzl_str,
            solution=solved,
            include_solved=include_solved
        )

        # call llm
        start = perf_counter()
        response = asyncio.run(call_llm(msgs, model=model_name))
        end = perf_counter()

        # parse results
        hint = extract_hint_fields(response)
        hint_str_pos = (hint.r-1)*9 + hint.c-1
        predicted_board = pzl_str[:hint_str_pos] + str(hint.value) + pzl_str[hint_str_pos+1:]

        logger.info(f"Took {end - start:.6f} seconds to predict square.")

        is_correct = is_valid_solution(predicted_board, solved)
        logger.info(f"Model correct: {is_correct}")
        logger.info(f"Predicted board:\n{predicted_board}")
        logger.info(f"Solved board:\n{solved}")

