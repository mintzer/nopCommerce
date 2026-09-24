using AwesomeAssertions;
using Moq;
using Nop.Core.Domain.Directory;
using Nop.Services.Directory;
using NUnit.Framework;

namespace Nop.Tests.Nop.Services.Tests.Directory;

[TestFixture]
public class UpdateExchangeRateTaskTests
{
    private Mock<ICurrencyService> _currencyServiceMock;
    private CurrencySettings _currencySettings;
    private UpdateExchangeRateTask _task;

    [SetUp]
    public void SetUp()
    {
        _currencyServiceMock = new Mock<ICurrencyService>();
        _currencySettings = new CurrencySettings();
        _task = new UpdateExchangeRateTask(_currencySettings, _currencyServiceMock.Object);
    }

    [Test]
    public async Task ExecuteAsync_AutoUpdateDisabled_ShouldNotFetchRates()
    {
        _currencySettings.AutoUpdateEnabled = false;

        await _task.ExecuteAsync();

        _currencyServiceMock.Verify(
            s => s.GetCurrencyLiveRatesAsync(It.IsAny<string>()),
            Times.Never);
    }

    [Test]
    public async Task ExecuteAsync_WithMatchingCurrencies_ShouldUpdateRatesAndTimestamps()
    {
        _currencySettings.AutoUpdateEnabled = true;

        var exchangeRates = new List<ExchangeRate>
        {
            new() { CurrencyCode = "USD", Rate = 1.2m },
            new() { CurrencyCode = "GBP", Rate = 0.86m }
        };

        var usd = new Currency { Id = 1, CurrencyCode = "USD", Rate = 1.0m };
        var gbp = new Currency { Id = 2, CurrencyCode = "GBP", Rate = 1.0m };

        _currencyServiceMock
            .Setup(s => s.GetCurrencyLiveRatesAsync(It.IsAny<string>()))
            .ReturnsAsync(exchangeRates);
        _currencyServiceMock
            .Setup(s => s.GetCurrencyByCodeAsync("USD"))
            .ReturnsAsync(usd);
        _currencyServiceMock
            .Setup(s => s.GetCurrencyByCodeAsync("GBP"))
            .ReturnsAsync(gbp);

        var beforeExecution = DateTime.UtcNow;

        await _task.ExecuteAsync();

        usd.Rate.Should().Be(1.2m);
        gbp.Rate.Should().Be(0.86m);
        usd.UpdatedOnUtc.Should().BeOnOrAfter(beforeExecution);
        gbp.UpdatedOnUtc.Should().BeOnOrAfter(beforeExecution);

        _currencyServiceMock.Verify(
            s => s.UpdateCurrencyAsync(usd),
            Times.Once);
        _currencyServiceMock.Verify(
            s => s.UpdateCurrencyAsync(gbp),
            Times.Once);
    }

    [Test]
    public async Task ExecuteAsync_UnknownCurrencyCode_ShouldSkipWithoutException()
    {
        _currencySettings.AutoUpdateEnabled = true;

        var exchangeRates = new List<ExchangeRate>
        {
            new() { CurrencyCode = "XYZ", Rate = 99.9m }
        };

        _currencyServiceMock
            .Setup(s => s.GetCurrencyLiveRatesAsync(It.IsAny<string>()))
            .ReturnsAsync(exchangeRates);
        _currencyServiceMock
            .Setup(s => s.GetCurrencyByCodeAsync("XYZ"))
            .ReturnsAsync((Currency)null);

        await _task.ExecuteAsync();

        _currencyServiceMock.Verify(
            s => s.UpdateCurrencyAsync(It.IsAny<Currency>()),
            Times.Never);
    }

    [Test]
    public async Task ExecuteAsync_EmptyRateList_ShouldNotUpdateAnyCurrency()
    {
        _currencySettings.AutoUpdateEnabled = true;

        _currencyServiceMock
            .Setup(s => s.GetCurrencyLiveRatesAsync(It.IsAny<string>()))
            .ReturnsAsync(new List<ExchangeRate>());

        await _task.ExecuteAsync();

        _currencyServiceMock.Verify(
            s => s.UpdateCurrencyAsync(It.IsAny<Currency>()),
            Times.Never);
    }

    [Test]
    public void ExecuteAsync_ProviderThrows_ShouldPropagateException()
    {
        _currencySettings.AutoUpdateEnabled = true;

        _currencyServiceMock
            .Setup(s => s.GetCurrencyLiveRatesAsync(It.IsAny<string>()))
            .ThrowsAsync(new InvalidOperationException("Provider unavailable"));

        var act = () => _task.ExecuteAsync();

        act.Should().ThrowAsync<InvalidOperationException>()
            .WithMessage("Provider unavailable");
    }
}
