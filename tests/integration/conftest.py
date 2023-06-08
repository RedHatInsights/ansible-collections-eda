from pathlib import Path
import subprocess

import pytest
from . import TESTS_PATH


@pytest.fixture(scope="function")
def run_rulebook(subprocess_teardown):
    def _run_rulebook(rules, env, envvars=""):
        args = [
            "ansible-rulebook", "-v",
            "--rulebook", rules,
            "--env-vars", envvars,
        ]

        proc = subprocess.Popen(
            args,
            cwd=TESTS_PATH,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        subprocess_teardown(proc)
        return proc

    return _run_rulebook


@pytest.fixture(scope="function")
def subprocess_teardown():
    processes = []

    def _teardown(process):
        processes.append(process)

    yield _teardown
    [proc.terminate() for proc in processes]


@pytest.fixture(scope="function")
def current_collection(tmp_path):
    """
    Symlink current collection in the temporary directory to be used within
    integration tests, set via ANSIBLE_COLLECTIONS_PATH env var.
    """
    namespace = tmp_path / "ansible_collections" / "redhatinsights"
    namespace.mkdir(parents=True)

    project_path = Path(TESTS_PATH) / ".." / ".."
    collection = namespace / "eda"
    collection.symlink_to(project_path.resolve(), target_is_directory=True)

    return tmp_path.resolve()
