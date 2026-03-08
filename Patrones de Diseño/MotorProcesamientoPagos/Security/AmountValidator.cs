// Security/AmountValidator.cs
using Configuration;
namespace Security
{
  public class AmountValidator : PaymentValidator
  {
    public override bool Validate(PaymentRequest request)
    {
      // Consultamos la verdad única del Singleton
      if (request.Amount > PaymentConfig.Instance.GlobalSecurityThreshold)
      {
        Console.WriteLine($"[Security] Rechazado: Monto {request.Amount} excede el límite.");
        return false;
      }

      return Next?.Validate(request) ?? true;
    }
  }
}

