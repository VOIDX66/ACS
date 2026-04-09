namespace Notifications.Domain.Interfaces
{
  public interface ITransactionObserver
  {
    void OnTransactionCompleted(Payments.Domain.Entities.PaymentRequest request, bool success);
  }
}