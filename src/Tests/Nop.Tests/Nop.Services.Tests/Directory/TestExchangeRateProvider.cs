using Nop.Core.Domain.Directory;
using Nop.Services.Directory;
using Nop.Services.Plugins;

namespace Nop.Tests.Nop.Services.Tests.Directory;

public class TestExchangeRateProvider : BasePlugin, IExchangeRateProvider
{
    /// <summary>
    /// Gets or sets the rates to return from <see cref="GetCurrencyLiveRatesAsync"/>.
    /// When non-null, these rates are returned instead of an empty list.
    /// Set to null (the default) to restore the original empty-list behavior.
    /// </summary>
    public static IList<ExchangeRate>? RatesToReturn { get; set; }

    /// <summary>
    /// Gets currency live rates
    /// </summary>
    /// <param name="exchangeRateCurrencyCode">Exchange rate currency code</param>
    /// <returns>Exchange rates</returns>
    public Task<IList<ExchangeRate>> GetCurrencyLiveRatesAsync(string exchangeRateCurrencyCode)
    {
        return Task.FromResult<IList<ExchangeRate>>(RatesToReturn ?? new List<ExchangeRate>());
    }
}