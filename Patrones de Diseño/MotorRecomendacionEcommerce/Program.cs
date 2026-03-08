using Reservations;
using Reservations.Notifications;
using Reservations.Pricing;
namespace Program
{
  class Program
  {
    static void Main(string[] args)
    {
      Console.WriteLine("=== AEROLÍNEA: SISTEMA DE RESERVAS ===");

      // 1. Uso del Builder para construir una reserva compleja
      var builder = new ReservationBuilder();

      var miReserva = builder
          .ConPasejero("VOID", "PASS-9988")
          .ParaVuelo("AV204", "12A")
          .ConPrecioBase(200.00m, new HolidayPricing()) // Inyectamos Strategy
          .AgregarServicioExtra("WiFi a bordo")
          .AgregarServicioExtra("Maleta extra")
          .Build();

      // 2. Suscribir Observadores
      miReserva.Subscribe(new EmailNotifier());
      miReserva.Subscribe(new SmsNotifier());

      // 3. Verificar Precio (Strategy)
      Console.WriteLine($"\nTotal a pagar (Dia Festivo): {miReserva.GetTotal():C}");

      // 4. Ciclo de Vida (State)
      Console.WriteLine("\n--- Iniciando Transiciones de Estado ---");

      // Intentar Check-In antes de pagar (Debería fallar según PendingState)
      try
      {
        miReserva.RealizarCheckIn();
      }
      catch (Exception ex)
      {
        Console.WriteLine($"[Error de Negocio]: {ex.Message}");
      }

      // Confirmar (Pasa de Pending a Confirmed)
      miReserva.Confirmar();

      // Ahora sí, Check-In
      miReserva.RealizarCheckIn();

      // Intentar Cancelar después de confirmar
      miReserva.Cancelar();

      // Intentar Confirmar una ya cancelada (Debería fallar según CancelledState)
      try
      {
        miReserva.Confirmar();
      }
      catch (Exception ex)
      {
        Console.WriteLine($"[Error de Negocio]: {ex.Message}");
      }

      Console.WriteLine("\n=======================================================");
    }
  }
}