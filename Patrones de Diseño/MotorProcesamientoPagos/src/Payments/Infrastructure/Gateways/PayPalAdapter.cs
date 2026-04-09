using Gateways.Domain.Interfaces;

namespace Payments.Infrastructure.Gateways
{
  public class PayPalAdapter : IPaymentGateway
  {
    public bool ProcessExternalPayment(decimal amount, string currency, string transactionId)
    {
      Console.WriteLine($"[PayPal Adapter] Iniciando flujo de aprobación Express Checkout...");
      Console.WriteLine($"[PayPal SDK] Executing: paypal.order.execute('{transactionId}')");
      return true;
    }
  }
}