//Reservations/LifeCycle/Interfaces/IReservationState.cs
namespace Reservations.LifeCycle
{
  // Definimos el contrato de los estados
  public interface IReservationState
  {
    void Confirmar(Reservation reservation);
    void Cancelar(Reservation reservation);
    void RealizarCheckIn(Reservation reservation);
  }
}