using Payments.Domain.Interfaces;
using Security.Infrastructure.Validators;
using Payments.Application.Services;
using Payments.Application.Services.Regions;

namespace Payments.Application.Factories
{
  public static class PaymentFactory
  {
    public static PaymentProcessor CreateProcessor(string country, PaymentValidator validator, ICurrencyConverter converter)
    {
      return country.ToUpper() switch
      {
        "ES" or "FR" or "DE" => new EuropeanProcessor(validator, converter),
        "US" or "CA" => new AmericanProcessor(validator, converter),
        _ => throw new NotSupportedException($"El país {country} no tiene un procesador asignado.")
      };
    }
  }
}