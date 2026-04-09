using Payments.Domain.Entities;
using Payments.Domain.Interfaces;
using Payments.Application.Factories;
using Security.Infrastructure.Validators;
using Configuration;
using Gateways.Domain.Interfaces;

namespace Payments.Application.Services
{
  public class PaymentService
  {
    private readonly PaymentValidator _validator;
    private readonly ICurrencyConverter _converter;
    private readonly List<Notifications.Domain.Interfaces.ITransactionObserver> _observers = new();

    public PaymentService(PaymentValidator validator, ICurrencyConverter converter)
    {
      _validator = validator;
      _converter = converter;
    }

    public void Pay(string method, decimal amount, string country, string customerType)
    {
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
        var processor = PaymentFactory.CreateProcessor(country, _validator, _converter);
        processor.Process(request);
        Notify(request, true);
      }
      catch (Exception ex)
      {
        Console.WriteLine($"[Service] Error crítico en el proceso: {ex.Message}");
        Notify(request, false);
      }
    }

    private void Notify(PaymentRequest request, bool success)
    {
      _observers.ForEach(o => o.OnTransactionCompleted(request, success));
    }

    public void Subscribe(Notifications.Domain.Interfaces.ITransactionObserver observer)
    {
      if (!_observers.Contains(observer))
      {
        _observers.Add(observer);
      }
    }
  }
}