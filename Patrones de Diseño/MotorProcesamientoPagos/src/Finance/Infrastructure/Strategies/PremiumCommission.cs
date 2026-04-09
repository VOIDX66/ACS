using Payments.Domain.Interfaces;

namespace Finance.Infrastructure.Strategies
{
  public class PremiumCommission : ICommissionStrategy
  {
    public decimal Calculate(decimal amount) => amount * 0.02m;
  }
}