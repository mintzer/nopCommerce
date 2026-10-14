"""Functional tests for UpdateExchangeRateTask integration tests.

These tests invoke `dotnet test` filtered to specific NUnit test methods
in UpdateExchangeRateTaskIntegrationTests.cs, which exercise the full
pipeline through the DI container and SQLite database:
  - Full pipeline with known rates (DI + SQLite)
  - Unchanged currencies remain unmodified
  - AutoUpdateEnabled guard at integration level
"""

import pytest
from conftest import run_dotnet_test, parse_test_result

FILTER_PREFIX = "FullyQualifiedName~UpdateExchangeRateTaskIntegrationTests"


class TestFullPipelineIntegration:
    """Verify the full task pipeline through DI container and SQLite database."""

    def test_full_pipeline_updates_currencies(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.ExecuteAsync_FullPipelineWithKnownRates_UpdatesCurrencyEntities",
            timeout=120,
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"

    def test_currencies_not_in_response_unchanged(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.ExecuteAsync_CurrenciesNotInProviderResponse_RemainUnchanged",
            timeout=120,
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"

    def test_auto_update_disabled_integration(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.ExecuteAsync_AutoUpdateDisabled_DoesNotUpdateAnyCurrency",
            timeout=120,
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"
