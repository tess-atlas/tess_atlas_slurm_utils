import os
import argparse
from datetime import datetime
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SLURM_STATS_FNAME = "jobstats.txt"
STATS_COMMAND = "sacct -S {start} -E {end} -u {user} -X -o 'jobname%-40,cputimeraw,State,MaxRSS' --parsable2 > " + SLURM_STATS_FNAME

SEC_IN_HR = 60.0 * 60.0


def create_slurm_stats_file(start: str, end: str, user: str, fname: str):
    """This function creates a file called jobstats.txt in the current directory
    which contains the job stats for the given user between the given dates.

    Useful for debugging/checking job stats.

    The file is created by running the following command:
    sacct -S {start} -E {end} -u {user} {extra_args} -o \
    'jobname%-40,cputimeraw,State,MaxRSS' --parsable2 > jobstats.txt

    - cputimeraw is the total CPU time used by the job in seconds.
    - MaxRSS is the maximum resident set size of all tasks in the job.
    - State is the current state of the job (e.g. COMPLETED, FAILED, TIMEOUT).

    :param start: Date in YYYY-MM-DD format
    :param end: Date in YYYY-MM-DD format (must be greater than start)
    :param user: username
    :param store_mem: yes is mem data to be stored
    """
    cmd = STATS_COMMAND.format(start=start, end=end, user=user)
    process = subprocess.Popen(cmd, shell=True)
    process.wait()
    data = __slurm_raw_data_to_dataframe()
    # remove all non 'toi' jobs
    data = data[data['JobName'].str.contains('toi')]
    data.to_csv(fname, index=False)
    plot_jobs_runtime_histogram(fname)
    os.remove(SLURM_STATS_FNAME)
    print(f"Jobstats saved in: {os.path.abspath(fname)}")


def plot_jobs_runtime_histogram(fname: str):
    """Plot a histogram of the job runtimes"""
    data = pd.read_csv(fname)
    total_cpu_hrs = data['CPUTimeRAW'].sum() / SEC_IN_HR
    data = data[data['State'] == 'COMPLETED']
    data = data[data['CPUTimeRAW'] > 0]
    hrs = data['CPUTimeRAW'] / SEC_IN_HR
    bins = np.geomspace(0.1, 8, 100)
    plt.hist(hrs, bins=bins)
    plt.xlabel("CPU Hrs")
    plt.ylabel("Count")
    plt.xscale('log')
    # add txtbox with the TOTAL CPU Hrs at top left corner
    plt.text(0.1, 0.9, f"Failed + passed job Hrs: {int(total_cpu_hrs):,}Hrs", transform=plt.gca().transAxes)
    plt.title("Histogram of CPU Hrs for all COMPLETED jobs")
    plt.tight_layout()
    plt.savefig(fname.replace(".csv", ".png"))


def __slurm_raw_data_to_dataframe() -> pd.DataFrame:
    """
    Returns dataframe with the following columns:
    JobName|CPUTimeRAW|State|MaxRSS
    """
    with open(SLURM_STATS_FNAME, 'r') as f:
        filecontents = f.read().split("\n")
    header = filecontents[0].split("|")
    data = filecontents[1:]
    data = [d for d in data if len(d) > 1]
    data = np.array([np.array(row.split("|")) for row in data])
    data = data.T
    data_dict = {header[i]: data[i] for i in range(len(header))}
    data = pd.DataFrame(data_dict)
    data['CPUTimeRAW'] = data['CPUTimeRAW'].astype('float64')
    return data


def __today() -> str:
    return datetime.today().strftime("%Y-%m-%d")


def main():
    parser = argparse.ArgumentParser("Create slurm stats file")
    parser.add_argument("--start", help="Start date in YYYY-MM-DD format", required=True, default="2020-01-01")
    parser.add_argument("--end", help="End date in YYYY-MM-DD format", required=True, default=__today())
    parser.add_argument("--user", help="Username", required=True, default="avajpeyi")
    parser.add_argument("--fname", help="Output filename", required=False, default="jobstats.csv")
    args = parser.parse_args()
    create_slurm_stats_file(args.start, args.end, args.user, args.fname)


if __name__ == "__main__":
    main()
