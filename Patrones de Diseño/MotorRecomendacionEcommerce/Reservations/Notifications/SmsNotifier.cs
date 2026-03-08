// Reservations/Notifications/SmsNotifier.cs
namespace Reservations.Notifications
{
  public class SmsNotifier : IReservationObserver
  {
    public void Update(Reservation reservation, string message)
    {
      // Enviamos un SMS
      Console.WriteLine($"\t[SMS] Enviando a {reservation.PassengerName}: {message}");
      Console.WriteLine($"\t\t--> Detalles: Vuelo {reservation.FlightNumber}, Asiento {reservation.SeatNumber} ");
    }
  }
}