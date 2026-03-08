namespace Gateways
{
  public static class GatewayFactory
  {
    public static IPaymentGateway Get(string method)
    {
      return method.ToLower() switch
      {
        "stripe" or "creditcard" => new StripeAdapter(),
        "paypal" or "digitalwallet" => new PayPalAdapter(),
        // Aquí escalaríamos a MercadoPago, CryptoAdapter, etc.
        _ => throw new NotSupportedException($"El método de pago '{method}' no está soportado.")
      };
    }
  }
}