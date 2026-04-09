namespace Payments.Domain.Interfaces
{
  public interface ICommissionStrategy
  {
    decimal Calculate(decimal amount);
  }
}