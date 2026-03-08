// Program.cs
using EntryPoints;
using Finance;
using Security;
using Notifications;
namespace Program
{
  class Program
  {
    static void Main(string[] args)
    {
      // 1. Setup de Dependencias (Composición de la Infraestructura)
      // Configuramos la Chain of Responsibility
      var security = new AmountValidator();
      security.SetNext(new RiskCountryValidator());

      // Instanciamos el Strategy de conversión
      var converter = new DefaultConverter();

      // 2. Inicialización de la Facade (Punto de entrada único)
      var engine = new PaymentFacade(security, converter);

      // 3. Registro Dinámico de Observadores (El enfoque que elegiste)
      // Aquí podrías agregar múltiples servicios sin tocar la Facade
      engine.Subscribe(new EmailNotificationObserver());
      engine.Subscribe(new SmsNotificationObserver());

      Console.WriteLine("======= SISTEMA DE PROCESAMIENTO INTERNACIONAL =======");

      // Caso 1: Flujo Feliz (Premium en Europa)
      // Usa EuropeanProcessor -> PremiumCommission (2%) -> StripeAdapter
      Console.WriteLine("\n[CASO 1: Pago Premium en España]");
      engine.Pay("Stripe", 450.00m, "ES", "Premium");

      // Caso 2: Violación de Seguridad (Monto Excedido)
      // Se detiene en AmountValidator (Límite configurado en el Singleton)
      Console.WriteLine("\n[CASO 2: Intento de Fraude - Monto Alto]");
      engine.Pay("PayPal", 15000.00m, "US", "Standard");

      // Caso 3: País de Riesgo
      // Se detiene en RiskCountryValidator (Lista negra del Singleton)
      Console.WriteLine("\n[CASO 3: Validación de Lista Negra]");
      engine.Pay("CreditCard", 100.00m, "NorthKorea", "Standard");

      // Caso 4: Transacción con Estrategia Internacional
      // Usa AmericanProcessor -> InternationalCommission (7% + 5.00) -> StripeAdapter
      Console.WriteLine("\n[CASO 4: Pago Internacional]");
      engine.Pay("Stripe", 1000.00m, "US", "International");

      // Caso 5: Error de Factory (Región no mapeada)
      // La Factory lanza la excepción y la Facade la captura para notificar el fallo
      Console.WriteLine("\n[CASO 5: Región No Soportada]");
      engine.Pay("Stripe", 50.00m, "JP", "Standard");

      Console.WriteLine("\n======================================================");
      Console.WriteLine("Presiona cualquier tecla para salir...");
      Console.ReadKey();
    }
  }
}