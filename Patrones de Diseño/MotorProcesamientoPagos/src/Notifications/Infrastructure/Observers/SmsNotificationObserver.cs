using Notifications.Domain.Interfaces;

namespace Notifications.Infrastructure.Observers
{
  public class SmsNotificationObserver : ITransactionObserver
  {
    public void OnTransactionCompleted(Payments.Domain.Entities.PaymentRequest request, bool success)
    {
      string status = success ? "Exitosa" : "Fallida";
      Console.WriteLine($"[Observer] Enviando Sms: La transacción {request.TransactionId} fue {status}.");
    }
  }
}