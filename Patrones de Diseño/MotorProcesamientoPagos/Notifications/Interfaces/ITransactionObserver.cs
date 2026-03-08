// Notifications/Interfaces/ITransactionObserver.cs
using Configuration;
namespace Notifications
{
  public interface ITransactionObserver
  {
    void OnTransactionCompleted(PaymentRequest request, bool success);
  }
}