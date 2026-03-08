// Gateways/StripeAdapter.cs
namespace Gateways
{
  public class StripeAdapter : IPaymentGateway
  {
    // Aquí podemos inyectar el SDK real de Stripe
    public bool ProcessExternalPayment(decimal amount, string currency, string transactionId)
    {
      Console.WriteLine($"[Stripe Adapter] Convirtiendo petición a formato Stripe...");
      Console.WriteLine($"[Stripe SDK] Calling: stripe.charges.create(amount: {amount * 100}, currency: '{currency}')");

      // Simulación de respuesta exitosa
      return true;
    }
  }
}

