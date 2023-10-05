import os
from typing import List

from .utils import mkdir, logger
from .file_generators import make_main_submitter, make_slurm_file
from .toi_data_interface import get_unprocessed_toi_numbers

MAX_ARRAY_SIZE = 2048

CMD = "srun run_toi ${ARRAY_ARGS[$SLURM_ARRAY_TASK_ID]} --outdir {outdir}"


def setup_jobs(
        toi_numbers: List[int],
        outdir: str,
        module_loads: str,
        submit: bool,
        clean: bool,
        email: str = "",
        skip_gen: bool = False,
        quickrun: bool = False,
        partition: str = "",
) -> None:
    """
    Set up and submit a batch of jobs for processing TOIs.

    Args:
        toi_numbers (list): List of TOI numbers to be processed.
        outdir (str): Output directory where job-related files will be stored.
        module_loads (str): Modules to be loaded before running the jobs.
        skip_gen (bool): Flag to skip generation jobs (True to skip, False to include).
        submit (bool): Flag to submit the jobs (True to submit, False to generate job files only).
        email (str): Email address for job notifications.
        partition (str): The compute cluster partition to use for job submission.

    Returns:
        None
    """

    initial_num, new_num = len(toi_numbers), len(toi_numbers)
    if not clean:
        toi_numbers = get_unprocessed_toi_numbers(toi_numbers, outdir)
        new_num = len(toi_numbers)

    msg = f"TOIs to be processed: {new_num}"
    if new_num != initial_num:
        msg += f" (not analyzing {initial_num - new_num}/{initial_num})"
    logger.info(msg)

    submit_dir = mkdir(outdir, "submit")
    toi_batches = [toi_numbers[i: i + MAX_ARRAY_SIZE] for i in range(0, len(toi_numbers), MAX_ARRAY_SIZE)]

    # Common keyword arguments for job generation
    kwargs = dict(
        outdir=outdir,
        module_loads=module_loads,
        submit_dir=submit_dir,
        email=email,
        array_job=True,
        command=CMD if not quickrun else CMD + " --quickrun"
    )

    generation_fns, analysis_fns = [], []
    for i, toi_batch in enumerate(toi_batches):
        kwargs.update(dict(array_args=toi_batch, jobid=i))
        gen_fn, anlys_fn = __generate_job_for_batch(kwargs.copy(), skip_gen)
        generation_fns.append(gen_fn)
        analysis_fns.append(anlys_fn)

    # Generate the main job submission file
    submit_file = make_main_submitter(generation_fns, analysis_fns, submit_dir, partition)

    # Submit or print the job submission command
    if submit:
        os.system(f"bash {submit_file}")
        logger.info("All submitted!")
    else:
        logger.info(f"To run job:\n>>> bash {submit_file}")


def __generate_job_for_batch(kwargs, skip_gen):
    cmd = kwargs.pop("command")
    gen_fname = None
    if not skip_gen:
        gen_fname = make_slurm_file(
            **kwargs,
            cpu_per_task=1,
            time="20:00",
            jobname=f"gen",
            mem="1000MB",
            command=f"{cmd} --setup",
        )

    analysis_fn = make_slurm_file(
        **kwargs,
        cpu_per_task=2,
        time="300:00",
        jobname=f"pe",
        mem="1500MB",
        tmp_mem="500M",
        command=cmd,
    )
    return gen_fname, analysis_fn
