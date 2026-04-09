using Payments.Domain.Entities;

namespace Payments.Domain.Interfaces
{
  public interface ICurrencyConverter
  {
    decimal Convert(decimal amount, string targetCurrency);
  }
}