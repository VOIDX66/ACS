using Payments.Domain.Interfaces;

namespace Finance.Infrastructure.Strategies
{
  public class StandardCommission : ICommissionStrategy
  {
    public decimal Calculate(decimal amount) => amount * 0.05m;
  }
}