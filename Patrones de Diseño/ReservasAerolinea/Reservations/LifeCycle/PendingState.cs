// Reservations/LifeCycle/PendingState.cs
namespace Reservations.LifeCycle
{
  // Estado inicial
  public class PendingState : IReservationState
  {
    public void Confirmar(Reservation context)
    {
      Console.WriteLine("--> Procesando pago y confirmando reserva...");
      // Cambiamos el estado
      context.TransitionTo(new ConfirmedState());
    }

    public void Cancelar(Reservation context)
    {
      Console.WriteLine("--> Cancelando reserva pendiente...");
      // Cambiamos el estado
      context.TransitionTo(new CancelledState());
    }

    public void RealizarCheckIn(Reservation context)
    {
      throw new InvalidOperationException("--> No se puede realizar check-in de una reserva pendiente");
    }
  }
}