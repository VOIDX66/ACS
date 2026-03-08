// Reservations/Notifications/Interfaces/IReservationObserver.cs
namespace Reservations.Notifications
{
  public interface IReservationObserver
  {
    void Update(Reservation reservation, string message);
  }
}