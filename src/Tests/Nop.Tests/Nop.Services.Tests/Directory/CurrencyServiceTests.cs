using AwesomeAssertions;
using Nop.Core.Domain.Directory;
using Nop.Services.Directory;
using NUnit.Framework;

namespace Nop.Tests.Nop.Services.Tests.Directory;

[TestFixture]
public class CurrencyServiceTests : ServiceTest<Currency>
{
    private ICurrencyService _currencyService;
    private IExchangeRatePluginManager _exchangeRatePluginManager;

    private Currency _currencyUsd, _currencyRur, _currencyEur;

    [OneTimeSetUp]
    public async Task SetUp()
    {
        _currencyService = GetService<ICurrencyService>();
        _exchangeRatePluginManager = GetService<IExchangeRatePluginManager>();

        _currencyEur = await _currencyService.GetCurrencyByCodeAsync("EUR");
        _currencyUsd = await _currencyService.GetCurrencyByCodeAsync("USD");
        _currencyRur = await _currencyService.GetCurrencyByCodeAsync("RUB");
    }

    [Test]
    public async Task GetCurrencyLiveRatesAsync_ShouldLoadPrimaryPluginAndDelegateToProvider()
    {
        var expectedRates = new List<ExchangeRate>
        {
            new() { CurrencyCode = "USD", Rate = 1.18m },
            new() { CurrencyCode = "GBP", Rate = 0.86m }
        };

        TestExchangeRateProvider.RatesToReturn = expectedRates;
        try
        {
            var rates = await _currencyService.GetCurrencyLiveRatesAsync();

            rates.Should().NotBeNull();
            rates.Should().HaveCount(2);
            rates[0].CurrencyCode.Should().Be("USD");
            rates[0].Rate.Should().Be(1.18m);
            rates[1].CurrencyCode.Should().Be("GBP");
            rates[1].Rate.Should().Be(0.86m);
        }
        finally
        {
            TestExchangeRateProvider.RatesToReturn = null;
        }
    }

    [Test]
    public async Task GetCurrencyByCodeAsync_ShouldMatchCaseInsensitively()
    {
        var byUpper = await _currencyService.GetCurrencyByCodeAsync("USD");
        var byLower = await _currencyService.GetCurrencyByCodeAsync("usd");
        var byMixed = await _currencyService.GetCurrencyByCodeAsync("Usd");

        byUpper.Should().NotBeNull();
        byLower.Should().NotBeNull();
        byMixed.Should().NotBeNull();
        byLower!.Id.Should().Be(byUpper!.Id);
        byMixed!.Id.Should().Be(byUpper.Id);
    }

    [Test]
    public async Task UpdateCurrencyAsync_ShouldPersistNewRateValue()
    {
        var currency = await _currencyService.GetCurrencyByCodeAsync("EUR");
        currency.Should().NotBeNull();

        var originalRate = currency!.Rate;
        var newRate = 99.1234m;

        currency.Rate = newRate;
        await _currencyService.UpdateCurrencyAsync(currency);
        try
        {
            var reloaded = await _currencyService.GetCurrencyByIdAsync(currency.Id);
            reloaded.Should().NotBeNull();
            reloaded!.Rate.Should().Be(newRate);
        }
        finally
        {
            currency.Rate = originalRate;
            await _currencyService.UpdateCurrencyAsync(currency);
        }
    }

    [Test]
    public async Task CanLoadExchangeRateProviders()
    {
        var providers = await _exchangeRatePluginManager.LoadAllPluginsAsync();
        providers.Should().NotBeNull();
        providers.Any().Should().BeTrue();
    }

    [Test]
    public async Task CanLoadExchangeRateProviderBySystemKeyword()
    {
        var provider = await _exchangeRatePluginManager.LoadPluginBySystemNameAsync("CurrencyExchange.TestProvider");
        provider.Should().NotBeNull();
    }

    [Test]
    public async Task CanLoadActiveExchangeRateProvider()
    {
        var provider = await _exchangeRatePluginManager.LoadPrimaryPluginAsync();
        provider.Should().NotBeNull();
    }

    [Test]
    public void CanConvertCurrency()
    {
        _currencyService.ConvertCurrency(10.1M, 1.5M).Should().Be(15.15M);
        _currencyService.ConvertCurrency(10.1M, 1).Should().Be(10.1M);
        _currencyService.ConvertCurrency(10.1M, 0).Should().Be(0);
        _currencyService.ConvertCurrency(0, 5).Should().Be(0);
    }

    [Test]
    public async Task CanConvertToPrimaryStoreCurrency()
    {
        var newCurrency = await _currencyService.ConvertToPrimaryStoreCurrencyAsync(8.686M, _currencyEur);
        newCurrency.Should().Be(10.1M);
        newCurrency = await _currencyService.ConvertToPrimaryStoreCurrencyAsync(638.825M, _currencyRur);
        newCurrency.Should().Be(10.1M);
        newCurrency = await _currencyService.ConvertToPrimaryStoreCurrencyAsync(759M, _currencyUsd);
        newCurrency.Should().Be(759M);
    }

    [Test]
    public async Task CanConvertFromPrimaryStoreCurrency()
    {
        var newCurrency = await _currencyService.ConvertFromPrimaryStoreCurrencyAsync(10.1M, _currencyEur);
        newCurrency.Should().Be(8.686M);
        newCurrency = await _currencyService.ConvertFromPrimaryStoreCurrencyAsync(10.1M, _currencyRur);
        newCurrency.Should().Be(638.825M);
        newCurrency = await _currencyService.ConvertFromPrimaryStoreCurrencyAsync(759M, _currencyUsd);
        newCurrency.Should().Be(759M);
    }

    protected override CrudData<Currency> CrudData
    {
        get
        {
            var insertItem = new Currency
            {
                Name = "Test name",
                CurrencyCode = "tn"
            };

            var updateItem = new Currency
            {
                Name = "Test name 1",
                CurrencyCode = "tn"
            };

            return new CrudData<Currency>
            {
                BaseEntity = insertItem,
                UpdatedEntity = updateItem,
                Insert = _currencyService.InsertCurrencyAsync,
                Update = _currencyService.UpdateCurrencyAsync,
                GetById = _currencyService.GetCurrencyByIdAsync,
                IsEqual = (item, other) => item.Name.Equals(other.Name),
                Delete = _currencyService.DeleteCurrencyAsync
            };
        }
    }
}