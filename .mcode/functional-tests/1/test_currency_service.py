"""Functional tests for CurrencyService call-chain integration tests.

These tests invoke `dotnet test` filtered to the new CurrencyServiceTests
methods added in this milestone, verifying:
  - GetCurrencyLiveRatesAsync delegates to provider via plugin manager
  - GetCurrencyByCodeAsync performs case-insensitive matching
  - UpdateCurrencyAsync persists rate changes
"""

import pytest
from conftest import run_dotnet_test, parse_test_result

FILTER_PREFIX = "FullyQualifiedName~CurrencyServiceTests"


class TestGetCurrencyLiveRates:
    """Verify GetCurrencyLiveRatesAsync loads the primary plugin and delegates."""

    def test_delegates_to_provider(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.GetCurrencyLiveRatesAsync_ShouldLoadPrimaryPluginAndDelegateToProvider"
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"


class TestGetCurrencyByCode:
    """Verify GetCurrencyByCodeAsync matches case-insensitively."""

    def test_case_insensitive_matching(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.GetCurrencyByCodeAsync_ShouldMatchCaseInsensitively"
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"


class TestUpdateCurrency:
    """Verify UpdateCurrencyAsync persists the new rate value."""

    def test_persists_new_rate(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.UpdateCurrencyAsync_ShouldPersistNewRateValue"
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"
