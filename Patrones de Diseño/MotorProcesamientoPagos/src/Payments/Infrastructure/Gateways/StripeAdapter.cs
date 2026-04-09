using Gateways.Domain.Interfaces;

namespace Payments.Infrastructure.Gateways
{
  public class StripeAdapter : IPaymentGateway
  {
    public bool ProcessExternalPayment(decimal amount, string currency, string transactionId)
    {
      Console.WriteLine($"[Stripe Adapter] Convirtiendo petición a formato Stripe...");
      Console.WriteLine($"[Stripe SDK] Calling: stripe.charges.create(amount: {amount * 100}, currency: '{currency}')");
      return true;
    }
  }
}