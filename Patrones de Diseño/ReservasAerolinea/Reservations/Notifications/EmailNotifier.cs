// Reservations/Notifications/EmailNotifier.cs
namespace Reservations.Notifications
{
  public class EmailNotifier : IReservationObserver
  {
    public void Update(Reservation reservation, string message)
    {
      // Enviamos un correo electronico
      Console.WriteLine($"\t[Email] Enviando a {reservation.PassengerName}: {message}");
      Console.WriteLine($"\t\t--> Detalles: Vuelo {reservation.FlightNumber}, Asiento {reservation.SeatNumber} ");
    }
  }
}