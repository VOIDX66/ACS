// Reservations/Reservation.cs
using Reservations.LifeCycle;
using Reservations.Pricing;
using Reservations.Notifications;
namespace Reservations
{
  public class Reservation
  {
    // Datos bases de la reserva
    public string PassengerName { get; set; } = string.Empty;
    public string PassportNumber { get; set; } = string.Empty;
    public string FlightNumber { get; set; } = string.Empty;
    public string SeatNumber { get; set; } = string.Empty;
    public decimal BasePrice { get; set; }
    public List<string> AdditionalServices { get; } = new();

    // Referencias a los Patrones Strategy y State
    public IPricingStrategy PricingStrategy { get; internal set; } = null!;
    private IReservationState _currentState;

    // Lista de Observadores
    private readonly List<IReservationObserver> _observers = new();

    public Reservation()
    {
      // Estado inicial por defecto
      _currentState = new PendingState();
    }

    // Logica del Patron Observer
    public void Subscribe(IReservationObserver observer)
    {
      // Verificamos si el observador ya esta suscrito
      if (!_observers.Contains(observer))
        _observers.Add(observer);
    }

    // Notificamos a todos los observadores
    private void Notify(string message)
    {
      _observers.ForEach(o => o.Update(this, message));
    }

    // Logica del Patron State
    // Delegamos la responsabilidad del cambio de comportamiento al State
    public void TransitionTo(IReservationState state)
    {
      _currentState = state;
      Notify($"Cambio de estado a {state.GetType().Name}");
    }

    public void Confirmar() => _currentState.Confirmar(this);
    public void Cancelar() => _currentState.Cancelar(this);
    public void RealizarCheckIn() => _currentState.RealizarCheckIn(this);

    // Logica del Patron Strategy
    public decimal GetTotal() => PricingStrategy.GetTotal(BasePrice);
  }
}