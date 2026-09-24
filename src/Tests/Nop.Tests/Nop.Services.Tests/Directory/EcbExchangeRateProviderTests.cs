using System.Net;
using System.Text;
using AwesomeAssertions;
using Moq;
using Nop.Core;
using Nop.Core.Http;
using Nop.Plugin.ExchangeRate.EcbExchange;
using Nop.Services.Configuration;
using Nop.Services.Localization;
using Nop.Services.Logging;
using NUnit.Framework;

namespace Nop.Tests.Nop.Services.Tests.Directory;

[TestFixture]
public class EcbExchangeRateProviderTests
{
    private const string ValidEcbXml = """
        <?xml version="1.0" encoding="UTF-8"?>
        <gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01" xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">
          <gesmes:subject>Reference rates</gesmes:subject>
          <gesmes:Sender><gesmes:name>European Central Bank</gesmes:name></gesmes:Sender>
          <Cube>
            <Cube time="2024-01-15">
              <Cube currency="USD" rate="1.0987"/>
              <Cube currency="GBP" rate="0.86163"/>
              <Cube currency="JPY" rate="161.12"/>
            </Cube>
          </Cube>
        </gesmes:Envelope>
        """;

    private EcbExchangeRateSettings _settings;
    private Mock<IHttpClientFactory> _httpClientFactoryMock;
    private Mock<ILocalizationService> _localizationServiceMock;
    private Mock<ILogger> _loggerMock;
    private Mock<ISettingService> _settingServiceMock;
    private EcbExchangeRateProvider _provider;

    [SetUp]
    public void SetUp()
    {
        _settings = new EcbExchangeRateSettings
        {
            EcbLink = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
        };
        _httpClientFactoryMock = new Mock<IHttpClientFactory>();
        _localizationServiceMock = new Mock<ILocalizationService>();
        _loggerMock = new Mock<ILogger>();
        _settingServiceMock = new Mock<ISettingService>();

        _localizationServiceMock
            .Setup(l => l.GetResourceAsync(It.IsAny<string>()))
            .ReturnsAsync("Currency not supported by ECB");

        _provider = new EcbExchangeRateProvider(
            _settings,
            _httpClientFactoryMock.Object,
            _localizationServiceMock.Object,
            _loggerMock.Object,
            _settingServiceMock.Object);
    }

    [Test]
    public async Task GetCurrencyLiveRatesAsync_EurBaseCurrency_ReturnsRatesDirectly()
    {
        SetupHttpClient(ValidEcbXml);

        var rates = await _provider.GetCurrencyLiveRatesAsync("EUR");

        rates.Should().HaveCount(4);
        rates.Single(r => r.CurrencyCode == "EUR").Rate.Should().Be(1.0m);
        rates.Single(r => r.CurrencyCode == "USD").Rate.Should().Be(1.0987m);
        rates.Single(r => r.CurrencyCode == "GBP").Rate.Should().Be(0.86163m);
        rates.Single(r => r.CurrencyCode == "JPY").Rate.Should().Be(161.12m);
    }

    [Test]
    public async Task GetCurrencyLiveRatesAsync_NonEurBaseCurrency_ReturnsCrossRates()
    {
        SetupHttpClient(ValidEcbXml);

        var rates = await _provider.GetCurrencyLiveRatesAsync("USD");

        rates.Should().HaveCount(4);

        var eurRate = rates.Single(r => r.CurrencyCode == "EUR");
        eurRate.Rate.Should().Be(Math.Round(1.0m / 1.0987m, 4));

        var usdRate = rates.Single(r => r.CurrencyCode == "USD");
        usdRate.Rate.Should().Be(Math.Round(1.0987m / 1.0987m, 4));

        var gbpRate = rates.Single(r => r.CurrencyCode == "GBP");
        gbpRate.Rate.Should().Be(Math.Round(0.86163m / 1.0987m, 4));

        var jpyRate = rates.Single(r => r.CurrencyCode == "JPY");
        jpyRate.Rate.Should().Be(Math.Round(161.12m / 1.0987m, 4));
    }

    [Test]
    public void GetCurrencyLiveRatesAsync_UnknownBaseCurrency_ThrowsNopException()
    {
        SetupHttpClient(ValidEcbXml);

        var act = () => _provider.GetCurrencyLiveRatesAsync("XYZ");

        act.Should().ThrowAsync<NopException>();
    }

    [Test]
    public async Task GetCurrencyLiveRatesAsync_DateParsing_SetsUpdatedOnFromXml()
    {
        SetupHttpClient(ValidEcbXml);

        var rates = await _provider.GetCurrencyLiveRatesAsync("EUR");

        var expectedDate = new DateTime(2024, 1, 15);
        foreach (var rate in rates)
        {
            rate.UpdatedOn.Should().Be(expectedDate);
        }
    }

    [Test]
    public async Task GetCurrencyLiveRatesAsync_NetworkFailure_LogsErrorAndReturnsEurEntry()
    {
        var handler = new MockHttpMessageHandler(_ =>
            throw new HttpRequestException("Network error"));
        var httpClient = new HttpClient(handler)
        {
            BaseAddress = new Uri("https://www.ecb.europa.eu")
        };
        _httpClientFactoryMock
            .Setup(f => f.CreateClient(NopHttpDefaults.DefaultHttpClient))
            .Returns(httpClient);

        var rates = await _provider.GetCurrencyLiveRatesAsync("EUR");

        rates.Should().HaveCount(1);
        rates[0].CurrencyCode.Should().Be("EUR");
        rates[0].Rate.Should().Be(1.0m);

        _loggerMock.Verify(
            l => l.ErrorAsync("ECB exchange rate provider", It.IsAny<Exception>(), null),
            Times.Once);
    }

    private void SetupHttpClient(string xmlContent)
    {
        var handler = new MockHttpMessageHandler(_ =>
            new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(xmlContent, Encoding.UTF8, "application/xml")
            });
        var httpClient = new HttpClient(handler)
        {
            BaseAddress = new Uri("https://www.ecb.europa.eu")
        };
        _httpClientFactoryMock
            .Setup(f => f.CreateClient(NopHttpDefaults.DefaultHttpClient))
            .Returns(httpClient);
    }

    private sealed class MockHttpMessageHandler : HttpMessageHandler
    {
        private readonly Func<HttpRequestMessage, HttpResponseMessage> _handler;

        public MockHttpMessageHandler(Func<HttpRequestMessage, HttpResponseMessage> handler)
        {
            _handler = handler;
        }

        protected override Task<HttpResponseMessage> SendAsync(
            HttpRequestMessage request,
            CancellationToken cancellationToken)
        {
            return Task.FromResult(_handler(request));
        }
    }
}
