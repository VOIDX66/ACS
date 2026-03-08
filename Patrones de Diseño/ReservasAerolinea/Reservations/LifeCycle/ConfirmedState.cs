// Reservations/LifeCycle/ConfirmedState.cs
namespace Reservations.LifeCycle
{
  public class ConfirmedState : IReservationState
  {
    public void Confirmar(Reservation context)
    {
      throw new InvalidOperationException("--> La reserva ya esta confirmada");
    }

    public void Cancelar(Reservation context)
    {
      Console.WriteLine("--> Cancelando reserva confirmada...\n\t--> Aplicando politica de reembolso...");
      // Cambiamos el estado
      context.TransitionTo(new CancelledState());
    }

    public void RealizarCheckIn(Reservation context)
    {
      Console.WriteLine("--> Check-in realizado con exito. !Disfrute su viaje!");
      // Cambiamos a otro estado si es necesario
      //context.TransitionTo(new CheckedInState());
    }
  }
}