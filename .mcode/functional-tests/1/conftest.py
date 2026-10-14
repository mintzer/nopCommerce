"""Shared fixtures and helpers for UpdateExchangeRateTask functional tests.

These tests invoke `dotnet test` with NUnit filters to exercise the
UpdateExchangeRateTask, CurrencyService, and EcbExchangeRateProvider code
paths through the nopCommerce test infrastructure (DI container + SQLite).
"""

import os
import subprocess
import re
import pytest

# Resolve to native Windows paths so MSBuild does not misinterpret /l2l/... as a switch.
_raw_ws = os.environ.get("WORKSPACE_DIR", r"C:\l2l\workspace")
WORKSPACE_DIR = os.path.abspath(_raw_ws)
REPO_DIR = os.path.join(WORKSPACE_DIR, "nopCommerce")
TEST_PROJECT = os.path.join(REPO_DIR, "src", "Tests", "Nop.Tests", "Nop.Tests.csproj")


def run_dotnet_test(filter_expr: str, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run `dotnet test` with the given NUnit filter and return the result.

    Args:
        filter_expr: NUnit/dotnet filter expression (e.g. FullyQualifiedName~ClassName.MethodName)
        timeout: Maximum seconds to wait for the test to complete.

    Returns:
        CompletedProcess with returncode, stdout, and stderr.
    """
    cmd = [
        "dotnet", "test", TEST_PROJECT,
        "--no-build",
        "--verbosity", "normal",
        "--filter", filter_expr,
    ]
    result = subprocess.run(
        cmd,
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result


def parse_test_result(stdout: str) -> dict:
    """Parse dotnet test output to extract pass/fail counts and duration.

    Returns:
        dict with keys: total, passed, failed, skipped, duration_ms, test_names
    """
    info = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "duration_ms": 0.0,
        "test_names": [],
        "passed_tests": [],
        "failed_tests": [],
    }

    # Extract individual test results
    for line in stdout.splitlines():
        line = line.strip()
        match_passed = re.match(r"Passed\s+(\S+)\s+\[(\d+)\s*ms\]", line)
        match_failed = re.match(r"Failed\s+(\S+)\s+\[(\d+)\s*ms\]", line)
        if match_passed:
            info["passed_tests"].append(match_passed.group(1))
            info["test_names"].append(match_passed.group(1))
        elif match_failed:
            info["failed_tests"].append(match_failed.group(1))
            info["test_names"].append(match_failed.group(1))

    # Extract summary line
    total_match = re.search(r"Total tests:\s*(\d+)", stdout)
    passed_match = re.search(r"Passed:\s*(\d+)", stdout)
    failed_match = re.search(r"Failed:\s*(\d+)", stdout)
    skipped_match = re.search(r"Skipped:\s*(\d+)", stdout)
    time_match = re.search(r"Total time:\s*([\d.]+)\s*Seconds", stdout)

    if total_match:
        info["total"] = int(total_match.group(1))
    if passed_match:
        info["passed"] = int(passed_match.group(1))
    if failed_match:
        info["failed"] = int(failed_match.group(1))
    if skipped_match:
        info["skipped"] = int(skipped_match.group(1))
    if time_match:
        info["duration_ms"] = float(time_match.group(1)) * 1000

    return info


@pytest.fixture(scope="session", autouse=True)
def verify_build():
    """Verify the solution is already built (we rely on pre-build via lifecycle)."""
    # The solution was built via lifecycle scripts before pytest runs.
    # Just verify the test DLL exists.
    test_dll = os.path.join(
        REPO_DIR, "src", "Tests", "Nop.Tests", "bin", "Debug", "net10.0", "Nop.Tests.dll"
    )
    assert os.path.exists(test_dll), (
        f"Test DLL not found at {test_dll}. Run lifecycle install+build first."
    )
