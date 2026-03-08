// Notifications/EmailNotificationObserver.cs
using Configuration;
namespace Notifications
{
  public class EmailNotificationObserver : ITransactionObserver
  {
    public void OnTransactionCompleted(PaymentRequest request, bool success)
    {
      string status = success ? "Exitosa" : "Fallida";
      Console.WriteLine($"[Observer] Enviando Email: La transacción {request.TransactionId} fue {status}.");
    }
  }
}