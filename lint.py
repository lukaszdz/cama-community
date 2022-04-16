""" Runs basic code quality check. Used during pre-commit """

import argparse
import logging
import sys

from pylint.lint import Run  # type: ignore

logging.getLogger().setLevel(logging.INFO)

parser = argparse.ArgumentParser(prog="LINT")

parser.add_argument(
    "-p",
    "--path",
    help="path to directory you want to run pylint | "
    "Default: %(default)s | "
    "Type: %(type)s ",
    default="./src",
    type=str,
)

parser.add_argument(
    "-t",
    "--threshold",
    help="score threshold to fail pylint runner | "
    "Default: %(default)s | "
    "Type: %(type)s ",
    default=7,
    type=float,
)


args = parser.parse_args()
path = str(args.path)
threshold = float(args.threshold)

logging.info(
    "PyLint Starting | " "Path: {} | " "Threshold: {} ".format(path, threshold)
)

results = Run([path], do_exit=False)

final_score = results.linter.stats.global_note

if final_score < threshold:

    MESSAGE = (
        "PyLint Failed | "
        "Score: {} | "
        "Threshold: {} ".format(final_score, threshold)
    )

    logging.error(MESSAGE)
    raise Exception(MESSAGE)

else:
    MESSAGE = (
        "PyLint Passed | "
        "Score: {} | "
        "Threshold: {} ".format(final_score, threshold)
    )

    logging.info(MESSAGE)

    sys.exit(0)
