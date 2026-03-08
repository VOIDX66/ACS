// Notifications/EmailNotificationObserver.cs
using Configuration;
namespace Notifications
{
  public class SmsNotificationObserver : ITransactionObserver
  {
    public void OnTransactionCompleted(PaymentRequest request, bool success)
    {
      string status = success ? "Exitosa" : "Fallida";
      Console.WriteLine($"[Observer] Enviando Sms: La transacción {request.TransactionId} fue {status}.");
    }
  }
}