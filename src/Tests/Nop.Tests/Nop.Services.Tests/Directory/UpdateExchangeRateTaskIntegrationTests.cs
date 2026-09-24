using AwesomeAssertions;
using Nop.Core.Domain.Directory;
using Nop.Services.Configuration;
using Nop.Services.Directory;
using NUnit.Framework;

namespace Nop.Tests.Nop.Services.Tests.Directory;

[TestFixture]
public class UpdateExchangeRateTaskIntegrationTests : ServiceTest
{
    private ICurrencyService _currencyService;
    private ISettingService _settingService;

    private string _originalProviderSystemName;
    private bool _originalAutoUpdateEnabled;
    private Dictionary<string, decimal> _originalRates;

    private static readonly string[] _allCurrencyCodes =
        ["USD", "AUD", "GBP", "CAD", "CNY", "EUR", "HKD", "JPY", "RUB", "SEK", "INR"];

    [SetUp]
    public async Task SetUp()
    {
        _currencyService = GetService<ICurrencyService>();
        _settingService = GetService<ISettingService>();

        var settings = await _settingService.LoadSettingAsync<CurrencySettings>();
        _originalProviderSystemName = settings.ActiveExchangeRateProviderSystemName;
        _originalAutoUpdateEnabled = settings.AutoUpdateEnabled;

        _originalRates = new Dictionary<string, decimal>();
        foreach (var code in _allCurrencyCodes)
        {
            var currency = await _currencyService.GetCurrencyByCodeAsync(code);
            if (currency != null)
                _originalRates[code] = currency.Rate;
        }
    }

    [TearDown]
    public async Task TearDown()
    {
        TestExchangeRateProvider.RatesToReturn = null;

        var settings = await _settingService.LoadSettingAsync<CurrencySettings>();
        settings.ActiveExchangeRateProviderSystemName = _originalProviderSystemName;
        settings.AutoUpdateEnabled = _originalAutoUpdateEnabled;
        await _settingService.SaveSettingAsync(settings);

        foreach (var (code, rate) in _originalRates)
        {
            var currency = await _currencyService.GetCurrencyByCodeAsync(code);
            if (currency != null)
            {
                currency.Rate = rate;
                await _currencyService.UpdateCurrencyAsync(currency);
            }
        }
    }

    private async Task<UpdateExchangeRateTask> CreateTaskWithFreshSettingsAsync()
    {
        // Resolve fresh instances so they pick up updated CurrencySettings from the DB
        var freshSettings = await _settingService.LoadSettingAsync<CurrencySettings>();
        var freshCurrencyService = GetService<ICurrencyService>();
        return new UpdateExchangeRateTask(freshSettings, freshCurrencyService);
    }

    [Test]
    public async Task ExecuteAsync_FullPipelineWithKnownRates_UpdatesCurrencyEntities()
    {
        var settings = await _settingService.LoadSettingAsync<CurrencySettings>();
        settings.AutoUpdateEnabled = true;
        settings.ActiveExchangeRateProviderSystemName = "CurrencyExchange.TestProvider";
        await _settingService.SaveSettingAsync(settings);

        TestExchangeRateProvider.RatesToReturn = new List<ExchangeRate>
        {
            new() { CurrencyCode = "EUR", Rate = 1.0m },
            new() { CurrencyCode = "GBP", Rate = 0.86m },
            new() { CurrencyCode = "JPY", Rate = 130.5m }
        };

        var beforeExecution = DateTime.UtcNow;

        var task = await CreateTaskWithFreshSettingsAsync();
        await task.ExecuteAsync();

        var eur = await _currencyService.GetCurrencyByCodeAsync("EUR");
        var gbp = await _currencyService.GetCurrencyByCodeAsync("GBP");
        var jpy = await _currencyService.GetCurrencyByCodeAsync("JPY");

        eur.Rate.Should().Be(1.0m);
        gbp.Rate.Should().Be(0.86m);
        jpy.Rate.Should().Be(130.5m);

        eur.UpdatedOnUtc.Should().BeOnOrAfter(beforeExecution);
        gbp.UpdatedOnUtc.Should().BeOnOrAfter(beforeExecution);
        jpy.UpdatedOnUtc.Should().BeOnOrAfter(beforeExecution);
    }

    [Test]
    public async Task ExecuteAsync_CurrenciesNotInProviderResponse_RemainUnchanged()
    {
        var settings = await _settingService.LoadSettingAsync<CurrencySettings>();
        settings.AutoUpdateEnabled = true;
        settings.ActiveExchangeRateProviderSystemName = "CurrencyExchange.TestProvider";
        await _settingService.SaveSettingAsync(settings);

        TestExchangeRateProvider.RatesToReturn = new List<ExchangeRate>
        {
            new() { CurrencyCode = "EUR", Rate = 999.99m }
        };

        var task = await CreateTaskWithFreshSettingsAsync();
        await task.ExecuteAsync();

        var usd = await _currencyService.GetCurrencyByCodeAsync("USD");
        var aud = await _currencyService.GetCurrencyByCodeAsync("AUD");
        var gbp = await _currencyService.GetCurrencyByCodeAsync("GBP");

        usd.Rate.Should().Be(_originalRates["USD"]);
        aud.Rate.Should().Be(_originalRates["AUD"]);
        gbp.Rate.Should().Be(_originalRates["GBP"]);
    }

    [Test]
    public async Task ExecuteAsync_AutoUpdateDisabled_DoesNotUpdateAnyCurrency()
    {
        var settings = await _settingService.LoadSettingAsync<CurrencySettings>();
        settings.AutoUpdateEnabled = false;
        settings.ActiveExchangeRateProviderSystemName = "CurrencyExchange.TestProvider";
        await _settingService.SaveSettingAsync(settings);

        TestExchangeRateProvider.RatesToReturn = new List<ExchangeRate>
        {
            new() { CurrencyCode = "EUR", Rate = 999.99m },
            new() { CurrencyCode = "GBP", Rate = 999.99m },
            new() { CurrencyCode = "JPY", Rate = 999.99m }
        };

        var task = await CreateTaskWithFreshSettingsAsync();
        await task.ExecuteAsync();

        var eur = await _currencyService.GetCurrencyByCodeAsync("EUR");
        var gbp = await _currencyService.GetCurrencyByCodeAsync("GBP");
        var jpy = await _currencyService.GetCurrencyByCodeAsync("JPY");

        eur.Rate.Should().Be(_originalRates["EUR"]);
        gbp.Rate.Should().Be(_originalRates["GBP"]);
        jpy.Rate.Should().Be(_originalRates["JPY"]);
    }
}
