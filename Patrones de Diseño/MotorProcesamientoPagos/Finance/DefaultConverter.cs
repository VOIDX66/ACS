// Finance/DefaultConverter.cs
using Configuration;
namespace Finance
{
  public class DefaultConverter : ICurrencyConverter
  {
    public decimal Convert(decimal amount, string targetCurrency)
    {
      // Accedemos al Singleton para obtener la base de datos
      var config = PaymentConfig.Instance;

      // Si la moneda de destino es la base, simplemente devolvemos el monto
      if (targetCurrency == config.DefaultCurrency)
        return amount;

      // Convertimos el monto a la moneda base
      return amount * config.BaseExchangeRate;
    }
  }
}
