// Finance/Interfaces/ICommissionStrategy.cs
namespace Finance
{
  public interface ICommissionStrategy
  {
    decimal Calculate(decimal amount);
  }
}