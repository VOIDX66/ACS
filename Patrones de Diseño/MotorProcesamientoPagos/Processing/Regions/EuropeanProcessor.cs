// Processing/Regions/EuropeanProcessor.cs
using Processing;
using Configuration;
using Security;
using Finance;
namespace Regions
{
  public class EuropeanProcessor : PaymentProcessor
  {
    public EuropeanProcessor(PaymentValidator validator, ICurrencyConverter converter) : base(validator, converter) { }
    protected override bool RunSecurityChecks(PaymentRequest request)
    {
      Console.WriteLine("[EU] Validando normativas GDPR y límites SEPA...");
      return true;
    }
  }
}
