using Finance;
using Regions;
using Security;

namespace Processing
{
  public static class PaymentFactory
  {
    public static PaymentProcessor CreateProcessor(string country, PaymentValidator validator, ICurrencyConverter converter)
    {
      return country.ToUpper() switch
      {
        "ES" or "FR" or "DE" => new EuropeanProcessor(validator, converter),
        "US" or "CA" => new AmericanProcessor(validator, converter), // Suponiendo que existe
        _ => throw new NotSupportedException($"El país {country} no tiene un procesador asignado.")
      };
    }
  }
}

