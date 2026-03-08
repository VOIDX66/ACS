// Security/RiskCountryValidator.cs
using Configuration;
namespace Security
{
  public class RiskCountryValidator : PaymentValidator
  {
    public override bool Validate(PaymentRequest request)
    {
      if (PaymentConfig.Instance.IsCountryRestricted(request.Country))
      {
        Console.WriteLine($"[Security] Rechazado: País {request.Country} en lista de alto riesgo.");
        return false;
      }

      return Next?.Validate(request) ?? true;
    }
  }
}

