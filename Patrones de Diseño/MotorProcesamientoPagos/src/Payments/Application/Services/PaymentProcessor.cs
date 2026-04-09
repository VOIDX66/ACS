using Payments.Domain.Entities;
using Payments.Domain.Interfaces;
using Payments.Application.Factories;
using Gateways.Domain.Interfaces;
using Finance.Infrastructure.Strategies;
using Security.Infrastructure.Validators;

namespace Payments.Application.Services
{
  public abstract class PaymentProcessor
  {
    protected readonly PaymentValidator _validator;
    protected readonly ICurrencyConverter _converter;

    public PaymentProcessor(PaymentValidator validator, ICurrencyConverter converter)
    {
      _validator = validator;
      _converter = converter;
    }

    public void Process(PaymentRequest request)
    {
      if (!_validator.Validate(request)) throw new Exception("Security Breach");

      decimal convertedAmount = _converter.Convert(request.Amount, request.Currency);

      decimal finalAmount = CalculateFees(request, convertedAmount);

      ExecuteTransaction(request, finalAmount);
    }

    protected virtual bool RunSecurityChecks(PaymentRequest request)
    {
      var amountCheck = new AmountValidator();
      var countryCheck = new RiskCountryValidator();

      amountCheck.SetNext(countryCheck);

      return amountCheck.Validate(request);
    }

    protected virtual decimal CalculateFees(PaymentRequest request, decimal convertedAmount)
    {
      ICommissionStrategy strategy = request.CustomerType switch
      {
        "Premium" => new PremiumCommission(),
        "International" => new InternationalCommission(),
        _ => new StandardCommission()
      };

      decimal comission = strategy.Calculate(request.Amount);

      return request.Amount + comission;
    }

    private void ExecuteTransaction(PaymentRequest request, decimal finalAmount)
    {
      IPaymentGateway gateway = GatewayFactory.Get(request.PaymentMethod);

      bool success = gateway.ProcessExternalPayment(
          finalAmount,
          request.Currency,
          request.TransactionId
      );

      if (!success) throw new Exception($"Fallo en la pasarela {request.PaymentMethod}");
    }

    protected virtual void SendNotifications(PaymentRequest request)
    {
      Console.WriteLine("Notificación estándar enviada.");
    }
  }
}