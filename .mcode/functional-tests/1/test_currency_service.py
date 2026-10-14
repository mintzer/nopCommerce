"""Functional tests for CurrencyService call-chain integration tests.

These tests invoke `dotnet test` filtered to the new CurrencyServiceTests
methods added in this milestone, verifying:
  - GetCurrencyLiveRatesAsync delegates to provider via plugin manager
  - GetCurrencyByCodeAsync performs case-insensitive matching
  - UpdateCurrencyAsync persists rate changes
"""

from conftest import assert_single_test_passes

FILTER_PREFIX = "FullyQualifiedName~CurrencyServiceTests"


class TestGetCurrencyLiveRates:
    """Verify GetCurrencyLiveRatesAsync loads the primary plugin and delegates."""

    def test_delegates_to_provider(self, verify_build):
        assert_single_test_passes(
            f"{FILTER_PREFIX}.GetCurrencyLiveRatesAsync_ShouldLoadPrimaryPluginAndDelegateToProvider"
        )


class TestGetCurrencyByCode:
    """Verify GetCurrencyByCodeAsync matches case-insensitively."""

    def test_case_insensitive_matching(self, verify_build):
        assert_single_test_passes(
            f"{FILTER_PREFIX}.GetCurrencyByCodeAsync_ShouldMatchCaseInsensitively"
        )


class TestUpdateCurrency:
    """Verify UpdateCurrencyAsync persists the new rate value."""

    def test_persists_new_rate(self, verify_build):
        assert_single_test_passes(
            f"{FILTER_PREFIX}.UpdateCurrencyAsync_ShouldPersistNewRateValue"
        )
