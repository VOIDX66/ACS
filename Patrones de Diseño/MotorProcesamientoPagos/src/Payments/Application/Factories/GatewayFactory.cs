using Gateways.Domain.Interfaces;
using Payments.Infrastructure.Gateways;

namespace Payments.Application.Factories
{
  public static class GatewayFactory
  {
    public static IPaymentGateway Get(string method)
    {
      return method.ToLower() switch
      {
        "stripe" or "creditcard" => new StripeAdapter(),
        "paypal" or "digitalwallet" => new PayPalAdapter(),
        _ => throw new NotSupportedException($"El método de pago '{method}' no está soportado.")
      };
    }
  }
}