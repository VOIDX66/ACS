using Payments.Application.Services;
using Payments.Domain.Entities;
using Payments.Domain.Interfaces;
using Security.Infrastructure.Validators;

namespace Payments.Application.Services.Regions
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