// Finance/StandarCommission.cs
namespace Finance
{
  // Estrategia para clientes estándar (Comisión base)
  public class StandardCommission : ICommissionStrategy
  {
    public decimal Calculate(decimal amount) => amount * 0.05m; // 5% de comisión
  }
}

