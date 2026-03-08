// Finance/PremiumCommission.cs
namespace Finance
{
  public class PremiumCommission : ICommissionStrategy
  {
    public decimal Calculate(decimal amount) => amount * 0.02m; // 2% de comisión
  }
}
// Estrategia para clientes Premium (Comisión reducida)
