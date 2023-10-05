import os
from typing import List, Optional

import jinja2
from jinja2 import Template

from .utils import get_python_source_command, to_str_list, mkdir

SLURM_TEMPLATE = "slurm_template.sh"
SUBMIT_TEMPLATE = "submit_template.sh"
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def __load_template(template_file: str) -> Template:
    template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIR)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_file)
    return template


def make_slurm_file(
        outdir: str,
        module_loads: str,
        jobname: str,
        cpu_per_task: int,
        time: str,
        mem: str,
        submit_dir: str,
        jobid: Optional[int] = None,
        array_args: Optional[List[int]] = None,
        array_job: Optional[bool] = False,
        command: Optional[str] = None,
        email: Optional[str] = "",
        tmp_mem: Optional[str] = "",
        account: Optional[str] = "",
) -> str:
    """Make a slurm file for submitting a job to the cluster

    :param outdir: Base output directory (will generate {outdir}/log_{jobname})
    :param module_loads: Module loads to include in the slurm file
    :param jobname: Name of the job
    :param cpu_per_task: Number of CPUs per task
    :param time: Time limit for the job
    :param mem: Memory limit for the job
    :param submit_dir: Directory to save the slurm file to
    :param jobid: Job ID (for array jobs)tail
    :param array_args: Array arguments (for array jobs)
    :param array_job: Whether the job is an array job
    :param command: Command to run
    :param email: Email address to send notifications to
    :param tmp_mem: Temporary mem (tmp dir accessible via $JOBFS) (eg 1000M, or 1G)
    :param account: Account to charge the job to


    """
    log_dir = os.path.abspath(mkdir(outdir, f"log_{jobname}"))
    common_kwargs = dict(
        jobname=f"toi_{jobname}",
        time=time,
        outdir=os.path.abspath(outdir),
        module_loads=module_loads,
        cpu_per_task=cpu_per_task,
        load_env=get_python_source_command(),
        mem=mem,
        array_job=str(array_job),
        command=command,
        email=email,
        tmp_mem=tmp_mem,
        account=account,
    )
    array_kwargs = dict(
        array_end=None,
        array_args=None,
        log_file=os.path.abspath(mkdir(log_dir, f"{jobname}_%j.log")),
    )
    if array_job:
        array_kwargs = dict(
            array_end=str(len(array_args) - 1),
            array_args=to_str_list(array_args),
            log_file=mkdir(log_dir, f"{jobname}_%A_%a.log"),
        )

    file_contents = __load_template(SLURM_TEMPLATE).render(
        **common_kwargs, **array_kwargs
    )

    jobid_str = f"_{jobid}" if jobid is not None else ""
    jobfile_name = os.path.join(submit_dir, f"slurm_{jobname}{jobid_str}_job.sh")
    with open(jobfile_name, "w") as f:
        f.write(file_contents)
    return os.path.abspath(jobfile_name)


def __remove_null_values(l):
    return [i for i in l if i is not None]


def make_main_submitter(generation_fns, analysis_fns, submit_dir, partition=''):
    """Make a submit.sh file which submits all the jobs"""
    generation_fns = __remove_null_values(generation_fns)
    analysis_fns = __remove_null_values(analysis_fns)

    template = __load_template(SUBMIT_TEMPLATE)
    file_contents = template.render(
        generation_fns=to_str_list(generation_fns),
        analysis_fns=to_str_list(analysis_fns),
        partition=partition,
    )
    subfn = os.path.join(submit_dir, "submit.sh")
    with open(subfn, "w") as f:
        f.write(file_contents)
    return os.path.abspath(subfn)
