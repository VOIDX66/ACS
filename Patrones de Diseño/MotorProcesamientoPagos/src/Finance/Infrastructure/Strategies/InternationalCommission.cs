using Payments.Domain.Interfaces;

namespace Finance.Infrastructure.Strategies
{
  public class InternationalCommission : ICommissionStrategy
  {
    public decimal Calculate(decimal amount) => (amount * 0.07m) + 5.0m;
  }
}