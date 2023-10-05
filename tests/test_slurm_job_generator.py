import os
import pytest
from tess_atlas_slurm_utils import slurm_job_generator
from tess_atlas_slurm_utils.slurm_job_generator import setup_jobs
from tess_atlas_slurm_utils import cli
from conftest import generate_toi_files

TEST_ARRAY_SIZE = 15


@pytest.fixture
def outdir(tmpdir):
    return tmpdir


def test_folder_and_file_generation(outdir, monkeypatch):
    # Mock the MAX_ARRAY_SIZE using pytest's monkeypatch
    monkeypatch.setattr(slurm_job_generator, "MAX_ARRAY_SIZE", TEST_ARRAY_SIZE)

    n_tois = 30
    assert slurm_job_generator.MAX_ARRAY_SIZE == TEST_ARRAY_SIZE
    setup_jobs(
        toi_numbers=[i for i in range(n_tois)],
        outdir=outdir,
        module_loads="mod 1",
        submit=False,
        clean=True,
    )

    # Check that the outdir has correct files and directories
    assert set(os.listdir(outdir)) == {'log_pe', 'log_gen', 'submit'}
    n_batches = n_tois // TEST_ARRAY_SIZE
    # Check that the slurmfiles created ['submit.sh', 'slurm_pe_{i}_job.sh', 'slurm_gen_{i}_job.sh']
    assert os.path.isfile(outdir / 'submit' / 'submit.sh')
    for i in range(n_batches):
        assert os.path.isfile(outdir / 'submit' / f'slurm_pe_{i}_job.sh')
        assert os.path.isfile(outdir / 'submit' / f'slurm_gen_{i}_job.sh')


def test_jobs_only_for_unanalysed_tois(outdir, caplog):
    caplog.set_level("INFO")
    tois = [i for i in range(100, 105)]
    # Generate the toi files (make it seem like they've been analysed)
    generate_toi_files(outdir, tois)
    new_toi_list = [i for i in range(100, 110)]
    setup_jobs(
        toi_numbers=new_toi_list,
        outdir=outdir,
        module_loads="mod 1",
        submit=False,
        clean=False,
    )
    # Check that the log message is correct
    n_tois_to_process = len(new_toi_list) - len(tois)
    n_tois_total = len(new_toi_list)
    n_tois_skipped = len(tois)
    assert f"TOIs to be processed: {n_tois_to_process} (not analyzing {n_tois_skipped}/{n_tois_total})" in caplog.text


def test_quickrun(outdir):
    setup_jobs(
        toi_numbers=[1], outdir=outdir,
        module_loads="mod 1", submit=False,
        clean=False, quickrun=True,
    )
    # check that outdir/submit/slurm_pe_0_job.sh contains the quickrun flag
    with open(outdir / 'submit' / 'slurm_gen_0_job.sh', 'r') as f:
        txt = f.read()
    assert '--quickrun' in txt
    assert '--setup' in txt


def test_cli(outdir, monkeypatch):
    monkeypatch.setattr('sys.argv', ['tess_atlas_slurm_utils', '--toi_number', '1', '--outdir', str(outdir)])
    cli.main()
    monkeypatch.setattr('sys.argv', ['tess_atlas_slurm_utils', '--outdir', str(outdir)])
    cli.main()
    monkeypatch.setattr('sys.argv', [
        'tess_atlas_slurm_utils',
        '--toi_csv', str(outdir / 'tois.csv'),
        '--outdir', str(outdir),
        '--quickrun'
    ])
    cli.main()
