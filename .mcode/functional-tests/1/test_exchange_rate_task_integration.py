"""Functional tests for UpdateExchangeRateTask integration tests.

These tests invoke `dotnet test` filtered to specific NUnit test methods
in UpdateExchangeRateTaskIntegrationTests.cs, which exercise the full
pipeline through the DI container and SQLite database:
  - Full pipeline with known rates (DI + SQLite)
  - Unchanged currencies remain unmodified
  - AutoUpdateEnabled guard at integration level
"""

from conftest import assert_single_test_passes

FILTER_PREFIX = "FullyQualifiedName~UpdateExchangeRateTaskIntegrationTests"


class TestFullPipelineIntegration:
    """Verify the full task pipeline through DI container and SQLite database."""

    def test_full_pipeline_updates_currencies(self, verify_build):
        assert_single_test_passes(
            f"{FILTER_PREFIX}.ExecuteAsync_FullPipelineWithKnownRates_UpdatesCurrencyEntities",
            timeout=120,
        )

    def test_currencies_not_in_response_unchanged(self, verify_build):
        assert_single_test_passes(
            f"{FILTER_PREFIX}.ExecuteAsync_CurrenciesNotInProviderResponse_RemainUnchanged",
            timeout=120,
        )

    def test_auto_update_disabled_integration(self, verify_build):
        assert_single_test_passes(
            f"{FILTER_PREFIX}.ExecuteAsync_AutoUpdateDisabled_DoesNotUpdateAnyCurrency",
            timeout=120,
        )
