"""This module interfaces with the TOI data."""
import glob
import os
import re
from typing import List, Optional, Union

import pandas as pd

from .utils import logger

__all__ = ["parse_toi_numbers", "get_unprocessed_toi_numbers"]

TOI_CSV = "https://tess-atlas.github.io/exofop_data/exofop_data.csv"
LK_AVAIL = "Lightcurve Available"
TOI_INT = "TOI int"  # 101


def __get_completed_toi_pe_results_paths(outdir: str) -> pd.DataFrame:
    """Get the paths to the netcdf files for all completed TOIs"""
    search_path = os.path.join(outdir, "toi_*_files/*.netcdf")
    netcdf_files = glob.glob(search_path)
    logger.info(f"Searching {search_path} --> {len(netcdf_files)} files found")
    regex = "toi_(\d+)_files"
    tois = [int(re.search(regex, f).group(1)) for f in netcdf_files]
    return pd.DataFrame(dict(TOI=tois, path=netcdf_files))


def get_unprocessed_toi_numbers(toi_numbers: List, outdir: str) -> List[int]:
    """Filter toi_numbers to only include those that have not been processed"""
    processed_tois = set(__get_completed_toi_pe_results_paths(outdir).TOI.values)
    tois = set(toi_numbers)
    return list(tois.difference(processed_tois))


def parse_toi_numbers(toi_csv: Union[str, None], toi_number: Union[int, None], outdir: str) -> List[int]:
    if toi_csv and toi_number is None:  # get TOI numbers from CSV (gets the latest TOI numbers)
        toi_numbers = __read_csv_toi_numbers(toi_csv)
    elif toi_csv is None and toi_number:  # get single TOI number
        toi_numbers = [toi_number]
    elif toi_csv is None and toi_number is None:  # get all TOIs
        toi_numbers = __make_toi_csv(os.path.join(outdir, "tois.csv"))
    else:
        raise ValueError(f"Cannot pass both toi-csv and toi-number")
    return toi_numbers


def __read_csv_toi_numbers(toi_csv: str) -> List[int]:
    return list(pd.read_csv(toi_csv).toi_numbers.values)


def __make_toi_csv(fname: str, toi_numbers: Optional[List[int]] = []) -> List[int]:
    if len(toi_numbers) == 0:
        data = pd.read_csv(TOI_CSV)[[TOI_INT, LK_AVAIL]]
        toi_numbers = data[data[LK_AVAIL] == True][TOI_INT].values
    toi_numbers = list(set([int(i) for i in toi_numbers]))
    data = pd.DataFrame(dict(toi_numbers=toi_numbers))
    data.to_csv(fname, index=False)
    return __read_csv_toi_numbers(fname)
