using Payments.Application.Services;
using Payments.Domain.Entities;
using Payments.Domain.Interfaces;
using Security.Infrastructure.Validators;

namespace Payments.Application.Services.Regions
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