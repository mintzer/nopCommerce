"""Helper script to run each NUnit test and record results via write_test_results.py."""

import os
import subprocess
import sys

WORKSPACE_DIR = os.path.abspath(os.environ.get("WORKSPACE_DIR", r"C:\l2l\workspace"))
SANDBOX_ROOT = os.environ.get("SANDBOX_ROOT", r"C:\l2l")
REPO_DIR = os.path.join(WORKSPACE_DIR, "nopCommerce")
TEST_PROJECT = os.path.join(REPO_DIR, "src", "Tests", "Nop.Tests", "Nop.Tests.csproj")
WRITE_RESULTS = os.path.join(SANDBOX_ROOT, ".claude", "skills", "sandbox-app-runner", "write_test_results.py")

# All tests to run: (test_name, nunit_filter, category, description)
TESTS = [
    # UpdateExchangeRateTask unit tests
    (
        "test_auto_update_disabled_no_fetch",
        "UpdateExchangeRateTaskTests.ExecuteAsync_AutoUpdateDisabled_ShouldNotFetchRates",
        "HAPPY_PATH",
        "ExecuteAsync is a no-op when AutoUpdateEnabled is false",
    ),
    (
        "test_matching_currencies_updated",
        "UpdateExchangeRateTaskTests.ExecuteAsync_WithMatchingCurrencies_ShouldUpdateRatesAndTimestamps",
        "HAPPY_PATH",
        "ExecuteAsync updates Rate and UpdatedOnUtc for matching currencies",
    ),
    (
        "test_unknown_currency_skipped",
        "UpdateExchangeRateTaskTests.ExecuteAsync_UnknownCurrencyCode_ShouldSkipWithoutException",
        "BOUNDARY",
        "Unknown currency codes are silently skipped without exception",
    ),
    (
        "test_empty_rate_list_no_updates",
        "UpdateExchangeRateTaskTests.ExecuteAsync_EmptyRateList_ShouldNotUpdateAnyCurrency",
        "BOUNDARY",
        "No UpdateCurrencyAsync calls when provider returns empty list",
    ),
    (
        "test_provider_exception_propagates",
        "UpdateExchangeRateTaskTests.ExecuteAsync_ProviderThrows_ShouldPropagateException",
        "BOUNDARY",
        "Provider exceptions propagate through ExecuteAsync unmodified",
    ),
    # Integration tests
    (
        "test_full_pipeline_updates_currencies",
        "UpdateExchangeRateTaskIntegrationTests.ExecuteAsync_FullPipelineWithKnownRates_UpdatesCurrencyEntities",
        "HAPPY_PATH",
        "Full pipeline via DI and SQLite updates currency entities with known rates",
    ),
    (
        "test_currencies_not_in_response_unchanged",
        "UpdateExchangeRateTaskIntegrationTests.ExecuteAsync_CurrenciesNotInProviderResponse_RemainUnchanged",
        "BOUNDARY",
        "Currencies not in provider response retain their original rates",
    ),
    (
        "test_auto_update_disabled_integration",
        "UpdateExchangeRateTaskIntegrationTests.ExecuteAsync_AutoUpdateDisabled_DoesNotUpdateAnyCurrency",
        "HAPPY_PATH",
        "AutoUpdateEnabled=false guard verified at integration level with SQLite",
    ),
    # ECB provider tests
    (
        "test_eur_base_returns_rates_directly",
        "EcbExchangeRateProviderTests.GetCurrencyLiveRatesAsync_EurBaseCurrency_ReturnsRatesDirectly",
        "HAPPY_PATH",
        "ECB provider returns direct rates for EUR base currency",
    ),
    (
        "test_non_eur_base_returns_cross_rates",
        "EcbExchangeRateProviderTests.GetCurrencyLiveRatesAsync_NonEurBaseCurrency_ReturnsCrossRates",
        "HAPPY_PATH",
        "ECB provider calculates cross-rates for non-EUR base using Math.Round(4)",
    ),
    (
        "test_unknown_base_throws_nop_exception",
        "EcbExchangeRateProviderTests.GetCurrencyLiveRatesAsync_UnknownBaseCurrency_ThrowsNopException",
        "BOUNDARY",
        "ECB provider throws NopException for unknown base currency",
    ),
    (
        "test_date_parsing_sets_updated_on",
        "EcbExchangeRateProviderTests.GetCurrencyLiveRatesAsync_DateParsing_SetsUpdatedOnFromXml",
        "HAPPY_PATH",
        "ECB provider parses date from XML and sets UpdatedOn on ExchangeRate DTOs",
    ),
    (
        "test_network_failure_logs_and_returns_eur",
        "EcbExchangeRateProviderTests.GetCurrencyLiveRatesAsync_NetworkFailure_LogsErrorAndReturnsEurEntry",
        "BOUNDARY",
        "ECB provider logs error and returns EUR entry on network failure",
    ),
    (
        "test_malformed_xml_logs_and_returns_eur",
        "EcbExchangeRateProviderTests.GetCurrencyLiveRatesAsync_MalformedXml_LogsErrorAndReturnsEurEntry",
        "BOUNDARY",
        "ECB provider logs error and returns EUR entry on malformed XML",
    ),
    # CurrencyService call-chain tests
    (
        "test_delegates_to_provider",
        "CurrencyServiceTests.GetCurrencyLiveRatesAsync_ShouldLoadPrimaryPluginAndDelegateToProvider",
        "HAPPY_PATH",
        "GetCurrencyLiveRatesAsync loads primary plugin and delegates to provider",
    ),
    (
        "test_case_insensitive_matching",
        "CurrencyServiceTests.GetCurrencyByCodeAsync_ShouldMatchCaseInsensitively",
        "HAPPY_PATH",
        "GetCurrencyByCodeAsync matches USD/usd/Usd to the same currency entity",
    ),
    (
        "test_persists_new_rate",
        "CurrencyServiceTests.UpdateCurrencyAsync_ShouldPersistNewRateValue",
        "HAPPY_PATH",
        "UpdateCurrencyAsync persists the new rate value in the database",
    ),
]


def run_test(nunit_filter: str) -> tuple:
    """Run a single NUnit test and return (exit_code, stdout, duration_ms)."""
    cmd = [
        "dotnet", "test", TEST_PROJECT,
        "--no-build",
        "--verbosity", "normal",
        "--filter", f"FullyQualifiedName~{nunit_filter}",
    ]
    import time
    start = time.time()
    result = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True, timeout=300)
    elapsed_ms = (time.time() - start) * 1000
    output = result.stdout + (("\n" + result.stderr) if result.stderr else "")
    return result.returncode, output, elapsed_ms


def record_result(name, exit_code, output, duration_ms, category, description):
    """Record a test result via write_test_results.py."""
    # Truncate output to 3500 chars for safety
    truncated = output[:3500] if len(output) > 3500 else output
    cmd = [
        sys.executable, WRITE_RESULTS,
        "--name", name,
        "--repo-type", "target",
        "--repo-name", "nopCommerce",
        "--category", category,
        "--command", "dotnet test",
        "--args", f"--filter {name}",
        "--actual-output", truncated,
        "--actual-exit-code", str(exit_code),
        "--expected-exit-code", "0",
        "--duration-ms", f"{duration_ms:.1f}",
        "--description", description,
    ]
    subprocess.run(cmd, check=True, timeout=30)


def main():
    passed = 0
    failed = 0
    for name, nunit_filter, category, description in TESTS:
        print(f"\n--- Running: {name} ---")
        try:
            exit_code, output, duration_ms = run_test(nunit_filter)
        except subprocess.TimeoutExpired:
            print(f"  TIMEOUT: {name} exceeded 300s limit")
            exit_code = 1
            output = "ERROR: Test timed out after 300s"
            duration_ms = 300_000.0

        if exit_code == 0 and "Test Run Successful" in output:
            status = "PASSED"
            passed += 1
        else:
            status = "FAILED"
            failed += 1

        print(f"  {status} (exit={exit_code}, {duration_ms:.0f}ms)")
        try:
            record_result(name, exit_code, output, duration_ms, category, description)
        except subprocess.CalledProcessError as exc:
            print(f"  WARNING: record_result failed for {name}: {exc}")

    print(f"\n=== SUMMARY: {passed + failed} total, {passed} passed, {failed} failed ===")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
