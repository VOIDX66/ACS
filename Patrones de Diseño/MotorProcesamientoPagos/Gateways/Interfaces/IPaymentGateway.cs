// Gateways/Interfaces/IPaymentGateway.cs
using Configuration;
namespace Gateways
{
  public interface IPaymentGateway
  {
    bool ProcessExternalPayment(decimal amount, string currency, string transactionId);
  }
}