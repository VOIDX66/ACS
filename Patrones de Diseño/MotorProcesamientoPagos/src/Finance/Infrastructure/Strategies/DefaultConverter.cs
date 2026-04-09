using Configuration;
using Payments.Domain.Interfaces;

namespace Finance.Infrastructure.Strategies
{
  public class DefaultConverter : ICurrencyConverter
  {
    public decimal Convert(decimal amount, string targetCurrency)
    {
      var config = PaymentConfig.Instance;

      if (targetCurrency == config.DefaultCurrency)
        return amount;

      return amount * config.BaseExchangeRate;
    }
  }
}