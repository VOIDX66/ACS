// Reservation/Pricing/EconomyPricing.cs
namespace Reservations.Pricing
{
  public class EconomyPricing : IPricingStrategy
  {
    // Precio base sin recargos
    public decimal GetTotal(decimal basePrice) => basePrice;
  }
}