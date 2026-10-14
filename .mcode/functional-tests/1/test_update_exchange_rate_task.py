"""Functional tests for UpdateExchangeRateTask unit tests.

These tests invoke `dotnet test` filtered to specific NUnit test methods
in UpdateExchangeRateTaskTests.cs, verifying the behavioral contract of
the UpdateExchangeRateTask:
  - AutoUpdateEnabled guard
  - Happy path rate/timestamp updates
  - Unknown currency handling
  - Empty results handling
  - Rate value accuracy
"""

from conftest import assert_single_test_passes

FILTER_PREFIX = "FullyQualifiedName~UpdateExchangeRateTaskTests"


class TestAutoUpdateDisabled:
    """Verify ExecuteAsync returns immediately when AutoUpdateEnabled is false."""

    def test_auto_update_disabled_no_fetch(self, verify_build):
        info = assert_single_test_passes(
            f"{FILTER_PREFIX}.ExecuteAsync_AutoUpdateDisabled_ShouldNotFetchRates"
        )
        assert "ExecuteAsync_AutoUpdateDisabled_ShouldNotFetchRates" in info["passed_tests"]


class TestHappyPath:
    """Verify the task updates rates and timestamps for matching currencies."""

    def test_matching_currencies_updated(self, verify_build):
        assert_single_test_passes(
            f"{FILTER_PREFIX}.ExecuteAsync_WithMatchingCurrencies_ShouldUpdateRatesAndTimestamps"
        )


class TestUnknownCurrency:
    """Verify unknown currency codes are silently skipped."""

    def test_unknown_currency_skipped(self, verify_build):
        assert_single_test_passes(
            f"{FILTER_PREFIX}.ExecuteAsync_UnknownCurrencyCode_ShouldSkipWithoutException"
        )


class TestEmptyResults:
    """Verify no updates when provider returns empty list."""

    def test_empty_rate_list_no_updates(self, verify_build):
        assert_single_test_passes(
            f"{FILTER_PREFIX}.ExecuteAsync_EmptyRateList_ShouldNotUpdateAnyCurrency"
        )


class TestRateValueAccuracy:
    """Verify exact Rate value from provider is stored on Currency without rounding."""

    def test_rate_value_stored_exactly(self, verify_build):
        assert_single_test_passes(
            f"{FILTER_PREFIX}.ExecuteAsync_RateValueAccuracy_ShouldStoreExactRateWithoutRounding"
        )
