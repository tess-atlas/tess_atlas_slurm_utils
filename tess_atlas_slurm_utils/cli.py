#!/usr/bin/env python

"""CLI for creating slurm jobs for analysing TOIs

If the outdir already has analysed TOIs, then slurm files for only the unanalysed TOIs generated.
"""

import argparse
import os

from .toi_data_interface import parse_toi_numbers
from .slurm_job_generator import setup_jobs

PROG = "make_slurm_jobs"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create slurm job for analysing TOIs (needs either toi-csv or toi-number)",
        prog=PROG,
        usage=f"{PROG} [--toi_csv <csv>] [--toi_number <toi_number>]",
    )
    parser.add_argument(
        "--toi_csv",
        default=None,
        help="CSV with the toi numbers to analyse (csv needs a column with `toi_numbers`)",
    )
    parser.add_argument(
        "--toi_number",
        type=int,
        help="The TOI number to be analysed (e.g. 103). Cannot be passed with toi-csv",
        default=None,
    )
    parser.add_argument(
        "--outdir",
        help=(
            "outdir for jobs. "
            "NOTE: If outdir already has analysed TOIs, (and the kwarg 'clean' not passed), "
            "then slurm files for only the TOIs w/o netcdf files generated)"
        ),
        default="tess_atlas_catalog",
    )
    parser.add_argument(
        "--clean",
        action="store_true",  # False by default
        help="Run all TOIs (even those that have completed analysis)",
    )
    parser.add_argument(
        "--module_loads",
        default="git/2.18.0 gcc/9.2.0 openmpi/4.0.2 python/3.8.5",
        help="String containing all module loads in one line (each module separated by a space)",
    )
    parser.add_argument(
        "--submit",
        action="store_true",  # False by default
        help="Submit once files created",
    )
    parser.add_argument(
        "--email",
        default="",
        help="email address to send job updates to (default: ''). If not passed, no emails sent.",
    )
    parser.add_argument(
        "--skip-gen",
        action="store_true",  # False by default
        help="Skip generation step. Just do the gen+analysis as one job.",
    )
    parser.add_argument(
        "--quickrun",
        action="store_true",  # False by default
        help="Adds the --quickrun flag to the run_toi command",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    toi_numbers = parse_toi_numbers(args.toi_csv, args.toi_number, args.outdir)
    setup_jobs(
        toi_numbers=toi_numbers,
        outdir=args.outdir,
        module_loads=args.module_loads,
        submit=args.submit,
        clean=args.clean,
        email=args.email,
        skip_gen=args.skip_gen
    )


if __name__ == "__main__":
    main()
