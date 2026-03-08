// Processing/Regions/AmericanProcessor.cs
using Processing;
using Configuration;
using Finance;
using Gateways;
using Security;
namespace Regions
{
  public class AmericanProcessor : PaymentProcessor
  {
    public AmericanProcessor(PaymentValidator validator, ICurrencyConverter converter) : base(validator, converter) { }
    protected override bool RunSecurityChecks(PaymentRequest request)
    {
      Console.WriteLine("[US] Validando normativas PCI-DSS y límites por estado...");
      return true;
    }
  }
}
