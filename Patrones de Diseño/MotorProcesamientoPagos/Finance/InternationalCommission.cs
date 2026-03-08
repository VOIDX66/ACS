// Finance/InternationalCommission.cs
namespace Finance
{
  // Estrategia Internacional (Comisión fija + porcentaje)
  public class InternationalCommission : ICommissionStrategy
  {
    public decimal Calculate(decimal amount) => (amount * 0.07m) + 5.0m;
  }
}