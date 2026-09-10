"""Builds the argparse CLI surface: 8 subcommands mirroring the Rust
clap definition (add, update, delete, list, summary, set-budget, export,
categories)."""

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cost-cap",
        description="Track your own spending the way an F1 team tracks its cost cap",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add", help="Add a new expense")
    add.add_argument("--description", required=True)
    add.add_argument("--amount", required=True, type=float)
    add.add_argument("--category", default=None)

    update = subparsers.add_parser("update", help="Update an existing expense")
    update.add_argument("--id", required=True, type=int, dest="id")
    update.add_argument("--description", default=None)
    update.add_argument("--amount", default=None, type=float)
    update.add_argument("--category", default=None)

    delete = subparsers.add_parser("delete", help="Delete an expense by id")
    delete.add_argument("--id", required=True, type=int, dest="id")

    list_cmd = subparsers.add_parser("list", help="List expenses")
    list_cmd.add_argument("--category", default=None)

    summary = subparsers.add_parser("summary", help="Show a spending summary")
    summary.add_argument("--month", default=None, type=int)

    set_budget = subparsers.add_parser("set-budget", help="Set a monthly cost cap")
    set_budget.add_argument("--month", required=True, type=int)
    set_budget.add_argument("--cap", required=True, type=float)

    export = subparsers.add_parser("export", help="Export expenses to CSV")
    export.add_argument("--output", default="expenses.csv")

    subparsers.add_parser("categories", help="List suggested categories")

    return parser
