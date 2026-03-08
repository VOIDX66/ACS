// EntryPoints/PaymentFacade.cs
using Configuration;
using Finance;
using Notifications;
using Processing;
using Security;

namespace EntryPoints
{
  public class PaymentFacade
  {
    private readonly PaymentValidator _validator;
    private readonly ICurrencyConverter _converter;
    private readonly List<ITransactionObserver> _observers = new();

    public PaymentFacade(PaymentValidator validator, ICurrencyConverter converter)
    {
      // Dependencias
      _validator = validator;
      _converter = converter;
    }

    public void Pay(string method, decimal amount, string country, string customerType)
    {
      // Crear el request
      var request = new PaymentRequest(
        Guid.NewGuid().ToString(),
        amount,
        PaymentConfig.Instance.DefaultCurrency,
        country,
        customerType,
        method
      );
      try
      {
        // Obtenemos el procesador correspondiente
        var processor = PaymentFactory.CreateProcessor(country, _validator, _converter);

        // Ejecutamos el flujo, dentro de estre processor es donde se usara adapter atraves de GatewayFactory
        processor.Process(request);

        Notify(request, true);
      }
      catch (Exception ex)
      {
        Console.WriteLine($"[Facade] Error crítico en el proceso: {ex.Message}");
        Notify(request, false);
      }
    }

    private void Notify(PaymentRequest request, bool success)
    {
      _observers.ForEach(o => o.OnTransactionCompleted(request, success));
    }

    public void Subscribe(ITransactionObserver observer)
    {
      if (!_observers.Contains(observer))
      {
        _observers.Add(observer);
      }
    }
  }
}