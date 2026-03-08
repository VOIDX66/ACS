// Reservations/LifeCycle/CancelledState.cs
namespace Reservations.LifeCycle
{
  public class CancelledState : IReservationState
  {
    public void Confirmar(Reservation context)
    {
      throw new InvalidOperationException(
        "--> No se puede confirmar una reserva cancelada. Por favor, inicie una nueva reserva"
        );
    }
    public void Cancelar(Reservation context)
    {
      throw new InvalidOperationException("--> La reserva ya esta cancelada");
    }

    public void RealizarCheckIn(Reservation context)
    {
      throw new InvalidOperationException("--> No se puede realizar check-in de una reserva cancelada");
    }
  }
}