import pytest
import os


def __generate_fake_files_for_toi(outdir, toi_int):
    """For a given toi number, generate tmp files that make it seem like the toi has been analysed"""
    toi_dir = os.path.join(outdir, f"toi_{toi_int}_files")
    os.makedirs(toi_dir)
    open(os.path.join(outdir, f"toi_{toi_int}.ipynb"), "a").close()
    open(os.path.join(toi_dir, f"toi_{toi_int}.netcdf"), "a").close()


def generate_toi_files(outdir, tois):
    for toi in tois:
        __generate_fake_files_for_toi(outdir, toi)
