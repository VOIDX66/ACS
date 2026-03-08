// Reservations/ReservationBuilder.csIPricingStrategy
using Reservations.Pricing;
namespace Reservations
{
  public class ReservationBuilder
  {
    private Reservation _reservation = new();

    public ReservationBuilder ConPasejero(string nombre, string pasaporte)
    {
      _reservation.PassengerName = nombre;
      _reservation.PassportNumber = pasaporte;
      return this;
    }

    public ReservationBuilder ParaVuelo(string numeroVuelo, string asiento)
    {
      _reservation.FlightNumber = numeroVuelo;
      _reservation.SeatNumber = asiento;
      return this;
    }

    public ReservationBuilder ConPrecioBase(decimal precio, IPricingStrategy estrategia)
    {
      _reservation.BasePrice = precio;
      _reservation.PricingStrategy = estrategia;
      return this;
    }

    public ReservationBuilder AgregarServicioExtra(string servicio)
    {
      _reservation.AdditionalServices.Add(servicio);
      return this;
    }

    public Reservation Build()
    {
      // Reglas de negocio minimas para la construccion
      // 1. No se puede construir una reserva sin pasajero
      if (string.IsNullOrEmpty(_reservation.PassengerName))
        throw new InvalidOperationException("No se puede construir una reserva sin pasajero");

      // 2. Toda reserva debe tener una estrategia de precio definida  
      if (_reservation.PricingStrategy == null)
        throw new InvalidOperationException("Toda reserva debe tener una estrategia de precio definida");

      // Clonamos la reserva para poder que el builder sea reutilizable
      var resultado = _reservation;
      _reservation = new();

      return resultado;
    }
  }
}