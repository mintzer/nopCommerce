"""Functional tests for EcbExchangeRateProvider tests.

These tests invoke `dotnet test` filtered to specific NUnit test methods
in EcbExchangeRateProviderTests.cs, verifying the ECB provider:
  - EUR base currency rate parsing
  - Non-EUR cross-rate calculations
  - Unknown base currency handling
  - XML date parsing
  - Network failure handling
  - Malformed XML handling
"""

from conftest import assert_single_test_passes

FILTER_PREFIX = "FullyQualifiedName~EcbExchangeRateProviderTests"


class TestEcbEurBase:
    """Verify ECB provider returns direct rates for EUR base."""

    def test_eur_base_returns_rates_directly(self, verify_build):
        assert_single_test_passes(
            f"{FILTER_PREFIX}.GetCurrencyLiveRatesAsync_EurBaseCurrency_ReturnsRatesDirectly"
        )


class TestEcbNonEurBase:
    """Verify ECB provider calculates cross-rates for non-EUR base."""

    def test_non_eur_base_returns_cross_rates(self, verify_build):
        assert_single_test_passes(
            f"{FILTER_PREFIX}.GetCurrencyLiveRatesAsync_NonEurBaseCurrency_ReturnsCrossRates"
        )


class TestEcbUnknownCurrency:
    """Verify ECB provider throws for unknown base currency."""

    def test_unknown_base_throws_nop_exception(self, verify_build):
        assert_single_test_passes(
            f"{FILTER_PREFIX}.GetCurrencyLiveRatesAsync_UnknownBaseCurrency_ThrowsNopException"
        )


class TestEcbDateParsing:
    """Verify ECB provider parses dates from XML correctly."""

    def test_date_parsing_sets_updated_on(self, verify_build):
        assert_single_test_passes(
            f"{FILTER_PREFIX}.GetCurrencyLiveRatesAsync_DateParsing_SetsUpdatedOnFromXml"
        )


class TestEcbNetworkFailure:
    """Verify ECB provider handles network failures gracefully."""

    def test_network_failure_logs_and_returns_eur(self, verify_build):
        assert_single_test_passes(
            f"{FILTER_PREFIX}.GetCurrencyLiveRatesAsync_NetworkFailure_LogsErrorAndReturnsEurEntry"
        )


class TestEcbMalformedXml:
    """Verify ECB provider handles malformed XML gracefully."""

    def test_malformed_xml_logs_and_returns_eur(self, verify_build):
        assert_single_test_passes(
            f"{FILTER_PREFIX}.GetCurrencyLiveRatesAsync_MalformedXml_LogsErrorAndReturnsEurEntry"
        )
