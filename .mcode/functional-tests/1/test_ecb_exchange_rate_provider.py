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

import pytest
from conftest import run_dotnet_test, parse_test_result

FILTER_PREFIX = "FullyQualifiedName~EcbExchangeRateProviderTests"


class TestEcbEurBase:
    """Verify ECB provider returns direct rates for EUR base."""

    def test_eur_base_returns_rates_directly(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.GetCurrencyLiveRatesAsync_EurBaseCurrency_ReturnsRatesDirectly"
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"


class TestEcbNonEurBase:
    """Verify ECB provider calculates cross-rates for non-EUR base."""

    def test_non_eur_base_returns_cross_rates(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.GetCurrencyLiveRatesAsync_NonEurBaseCurrency_ReturnsCrossRates"
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"


class TestEcbUnknownCurrency:
    """Verify ECB provider throws for unknown base currency."""

    def test_unknown_base_throws_nop_exception(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.GetCurrencyLiveRatesAsync_UnknownBaseCurrency_ThrowsNopException"
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"


class TestEcbDateParsing:
    """Verify ECB provider parses dates from XML correctly."""

    def test_date_parsing_sets_updated_on(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.GetCurrencyLiveRatesAsync_DateParsing_SetsUpdatedOnFromXml"
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"


class TestEcbNetworkFailure:
    """Verify ECB provider handles network failures gracefully."""

    def test_network_failure_logs_and_returns_eur(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.GetCurrencyLiveRatesAsync_NetworkFailure_LogsErrorAndReturnsEurEntry"
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"


class TestEcbMalformedXml:
    """Verify ECB provider handles malformed XML gracefully."""

    def test_malformed_xml_logs_and_returns_eur(self, verify_build):
        result = run_dotnet_test(
            f"{FILTER_PREFIX}.GetCurrencyLiveRatesAsync_MalformedXml_LogsErrorAndReturnsEurEntry"
        )
        info = parse_test_result(result.stdout)
        assert result.returncode == 0, (
            f"dotnet test exited {result.returncode}.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )
        assert info["passed"] == 1, f"Expected 1 passed test, got {info}"
