// Reservations/Pricing/HolidayPricing.cs
namespace Reservations.Pricing
{
  public class HolidayPricing : IPricingStrategy
  {
    // Recargo por dias festivos
    public decimal GetTotal(decimal basePrice) => basePrice * 2;
  }
}