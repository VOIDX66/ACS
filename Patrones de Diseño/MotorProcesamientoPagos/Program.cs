using Payments.Application.Services;
using Finance.Infrastructure.Strategies;
using Security.Infrastructure.Validators;
using Notifications.Infrastructure.Observers;

namespace Presentation
{
  class Program
  {
    static void Main(string[] args)
    {
      var security = new AmountValidator();
      security.SetNext(new RiskCountryValidator());

      var converter = new DefaultConverter();

      var engine = new PaymentService(security, converter);

      engine.Subscribe(new EmailNotificationObserver());
      engine.Subscribe(new SmsNotificationObserver());

      Console.WriteLine("======= SISTEMA DE PROCESAMIENTO INTERNACIONAL =======");

      Console.WriteLine("\n[CASO 1: Pago Premium en España]");
      engine.Pay("Stripe", 450.00m, "ES", "Premium");

      Console.WriteLine("\n[CASO 2: Intento de Fraude - Monto Alto]");
      engine.Pay("PayPal", 15000.00m, "US", "Standard");

      Console.WriteLine("\n[CASO 3: Validación de Lista Negra]");
      engine.Pay("CreditCard", 100.00m, "NorthKorea", "Standard");

      Console.WriteLine("\n[CASO 4: Pago Internacional]");
      engine.Pay("Stripe", 1000.00m, "US", "International");

      Console.WriteLine("\n[CASO 5: Región No Soportada]");
      engine.Pay("Stripe", 50.00m, "JP", "Standard");

      Console.WriteLine("\n======================================================");
      Console.WriteLine("Presiona cualquier tecla para salir...");
      Console.ReadKey();
    }
  }
}