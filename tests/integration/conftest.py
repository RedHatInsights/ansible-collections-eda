import os
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
