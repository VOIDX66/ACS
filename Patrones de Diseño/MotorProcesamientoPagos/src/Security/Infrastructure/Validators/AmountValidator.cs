using Configuration;

namespace Security.Infrastructure.Validators
{
  public class AmountValidator : PaymentValidator
  {
    public override bool Validate(Payments.Domain.Entities.PaymentRequest request)
    {
      if (request.Amount > PaymentConfig.Instance.GlobalSecurityThreshold)
      {
        Console.WriteLine($"[Security] Rechazado: Monto {request.Amount} excede el límite.");
        return false;
      }

      return Next?.Validate(request) ?? true;
    }
  }
}