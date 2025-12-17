import argparse
from sudokusage_eval.runners.sample import run_sample


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="sudokusage-eval",
        description="Evaluation CLI for SudokuSage experiments",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sample_p = sub.add_parser("sample", help="Run sampling experiment")
    sample_p.add_argument("--model", default="gpt-5-nano")
    sample_p.add_argument("--difficulty", type=float, default=0.5)
    sample_p.add_argument("--samples", type=int, default=1)

    sample_p.add_argument(
        "--out",
        type=str,
        default=None,
        help="Optional CSV filepath to write per-sample results",
    )

    sample_p.add_argument(
        "--include-solved",
        dest="include_solved",
        action="store_true",
        default=True,
        help="Include the solved board in the prompt (default: on)",
    )
    sample_p.add_argument(
        "--no-include-solved",
        dest="include_solved",
        action="store_false",
        help="Do not include the solved board in the prompt",
    )

    args = parser.parse_args()

    if args.command == "sample":
        try:
            diff = float(args.difficulty)
        except ValueError:
            print("Error: --difficulty must be a float between 0.0 and 1.0")
            return 1
        
        if diff < 0.0 or diff > 1.0:
            print("Error: --difficulty must be between 0.0 and 1.0")
            return 1

        run_sample(
            model_name=args.model,
            difficulty=diff,
            samples=args.samples,
            include_solved=args.include_solved,
            out=args.out,
        )

    return 0
