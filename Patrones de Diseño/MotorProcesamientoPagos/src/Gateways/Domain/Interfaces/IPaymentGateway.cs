using Payments.Domain.Entities;

namespace Gateways.Domain.Interfaces
{
  public interface IPaymentGateway
  {
    bool ProcessExternalPayment(decimal amount, string currency, string transactionId);
  }
}