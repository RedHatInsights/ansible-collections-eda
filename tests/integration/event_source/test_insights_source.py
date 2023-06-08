import os
import subprocess
import time
import json

import pytest_check
import requests
from ...integration import TESTS_PATH


def wait_for_events(proc: subprocess.Popen, timeout: float = 10.0):
    """
    Wait for events to be processed by ansible-rulebook, or timeout.
    Requires the process to be running in debug mode.
    """
    start = time.time()
    while stdout := proc.stdout.readline().decode():
        print(stdout)
        if "Waiting for events" in stdout:
            break
        time.sleep(0.1)
        if time.time() - start > timeout:
            raise TimeoutError("Timeout waiting for events")


def test_insights_source_sanity(run_rulebook, current_collection):
    """
    Check successful execution, response and shutdown
    of the Insights source plugin.
    """
    msgs = [
        json.dumps({"eventdata": "insights"}).encode("ascii"),
        json.dumps({"shutdown": ""}).encode("ascii"),
    ]

    port = 5000
    url = f"http://127.0.0.1:{port}/endpoint"

    env = os.environ.copy()
    env["ANSIBLE_COLLECTIONS_PATH"] = str(current_collection)
    env["WH_PORT"] = str(port)
    env["SECRET"] = "secret"

    rules = TESTS_PATH + "/event_source/test_insights_rules.yaml"

    proc = run_rulebook(rules, env, envvars="WH_PORT,SECRET")
    wait_for_events(proc)

    for msg in msgs:
        headers = {"X-Insight-Token": "secret"}
        requests.post(url, data=msg, headers=headers)

    try:
        stdout, _unused_stderr = proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        proc.terminate()
        stdout, _unused_stderr = proc.communicate()

    assert "Rule fired successfully" in stdout.decode()
    assert "eventdata" in stdout.decode()
    assert proc.returncode == 0


def test_insights_source_unauthorized(run_rulebook, current_collection):
    """
    Check successful execution, response and shutdown
    of the Insights source plugin.
    """
    port = 5000
    url = f"http://127.0.0.1:{port}/endpoint"

    env = os.environ.copy()
    env["ANSIBLE_COLLECTIONS_PATH"] = str(current_collection)
    env["WH_PORT"] = str(port)
    env["SECRET"] = "secret"

    rules = TESTS_PATH + "/event_source/test_insights_rules.yaml"

    proc = run_rulebook(rules, env, envvars="WH_PORT,SECRET")
    wait_for_events(proc)

    headers_list = [
        {},
        {"Authorization": "Bearer badtoken"},
        {"X-Insight-Token": "badtoken"}
    ]

    for headers in headers_list:
        msg = json.dumps({"eventdata": "insights"}).encode("ascii")
        resp = requests.post(url, data=msg, headers=headers)
        with pytest_check.check:
            assert resp.status_code == 401, f"unauthorized not returned for headers {headers}"

    try:
        stdout, _unused_stderr = proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        proc.terminate()
        stdout, _unused_stderr = proc.communicate()

    assert "Rule fired successfully" not in stdout.decode()
    assert "eventdata" not in stdout.decode()
