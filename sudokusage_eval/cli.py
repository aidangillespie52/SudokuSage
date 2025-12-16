import argparse
from sudokusage_eval.runners.sample import run_sample

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="sudokusage-eval",
        description="Evaluation CLI for SudokuSage experiments"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sample_p = sub.add_parser("sample", help="Run sampling experiment")
    sample_p.add_argument("--model", default="gpt-5-nano")
    sample_p.add_argument("--difficulty", type=float, default=0.5)
    sample_p.add_argument("--samples", type=int, default=1)

    args = parser.parse_args()

    if args.difficulty < 0.0 or args.difficulty > 1.0:
        print("Error: --difficulty must be between 0.0 and 1.0")
        return 1
    
    if args.command == "sample":
        run_sample(
            model_name=args.model,
            difficulty=args.difficulty,
            samples=args.samples,
        )

    return 0
