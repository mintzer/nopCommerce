"""Functional tests for UpdateExchangeRateTask unit tests.

These tests invoke `dotnet test` filtered to specific NUnit test methods
in UpdateExchangeRateTaskTests.cs, verifying the behavioral contract of
the UpdateExchangeRateTask:
  - AutoUpdateEnabled guard
  - Happy path rate/timestamp updates
  - Unknown currency handling
  - Empty results handling
  - Exception propagation
"""

from conftest import run_dotnet_test, parse_test_result

FILTER_PREFIX = "FullyQualifiedName~UpdateExchangeRateTaskTests"


class TestAutoUpdateDisabled:
    """Verify ExecuteAsync returns immediately when AutoUpdateEnabled is false."""

    def test_auto_update_disabled_no_fetch(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.ExecuteAsync_AutoUpdateDisabled_ShouldNotFetchRates"
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"
        assert "ExecuteAsync_AutoUpdateDisabled_ShouldNotFetchRates" in info["passed_tests"]


class TestHappyPath:
    """Verify the task updates rates and timestamps for matching currencies."""

    def test_matching_currencies_updated(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.ExecuteAsync_WithMatchingCurrencies_ShouldUpdateRatesAndTimestamps"
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"


class TestUnknownCurrency:
    """Verify unknown currency codes are silently skipped."""

    def test_unknown_currency_skipped(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.ExecuteAsync_UnknownCurrencyCode_ShouldSkipWithoutException"
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"


class TestEmptyResults:
    """Verify no updates when provider returns empty list."""

    def test_empty_rate_list_no_updates(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.ExecuteAsync_EmptyRateList_ShouldNotUpdateAnyCurrency"
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"


class TestExceptionPropagation:
    """Verify provider exceptions propagate through ExecuteAsync."""

    def test_provider_exception_propagates(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.ExecuteAsync_ProviderThrows_ShouldPropagateException"
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"
