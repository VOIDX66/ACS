// Reservations/Pricing/Interfaces/IPricingStrategy.cs
namespace Reservations.Pricing
{
  public interface IPricingStrategy
  {
    decimal GetTotal(decimal basePrice);
  }
}