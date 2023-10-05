# TESS-Atlas Slurm Utils
[![Coverage Status](https://coveralls.io/repos/github/tess-atlas/tess_atlas_slurm_utils/badge.svg?branch=main)](https://coveralls.io/github/tess-atlas/tess_atlas_slurm_utils?branch=main)

A slurm script generation script for tess-atlas.

## Usage
```
❯ make_slurm_job --help
usage: make_slurm_jobs [--toi_csv <csv>] [--toi_number <toi_number>]

Create slurm job for analysing TOIs (needs either toi-csv or toi-number)

optional arguments:
  -h, --help            show this help message and exit
  --toi_csv TOI_CSV     CSV with the toi numbers to analyse (csv needs a column with `toi_numbers`)
  --toi_number TOI_NUMBER
                        The TOI number to be analysed (e.g. 103). Cannot be passed with toi-csv
  --outdir OUTDIR       outdir for jobs. NOTE: If outdir already has analysed TOIs, (and the kwarg 'clean' not passed), then slurm files for only the TOIs w/o netcdf files
                        generated)
  --clean               Run all TOIs (even those that have completed analysis)
  --module_loads MODULE_LOADS
                        String containing all module loads in one line (each module separated by a space)
  --submit              Submit once files created
  --email EMAIL         email address to send job updates to (default: ''). If not passed, no emails sent.
  --skip-gen            Skip generation step. Just do the gen+analysis as one job.
  --quickrun            Adds the --quickrun flag to the run_toi command (only meant for testing)

```
