// Processing/PaymentProcessor.cs
using Configuration;
using Gateways;
using Finance;
using Security;

namespace Processing
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
    // El "Template Method": define la secuencia invariable
    public void Process(PaymentRequest request)
    {
      // 1. CoR
      if (!_validator.Validate(request)) throw new Exception("Security Breach");

      // 2. Strategy de Conversión
      decimal convertedAmount = _converter.Convert(request.Amount, request.Currency);

      // 3. Strategy de Comisión
      decimal finalAmount = CalculateFees(request, convertedAmount);

      // 4. Adapter
      ExecuteTransaction(request, finalAmount);
    }

    // Pasos que las regiones DEBEN implementar
    protected virtual bool RunSecurityChecks(PaymentRequest request)
    {
      // 1. Construimos la cadena (esto podría automatizarse, pero así es claro)
      var amountCheck = new AmountValidator();
      var countryCheck = new RiskCountryValidator();

      amountCheck.SetNext(countryCheck);

      // 2. Iniciamos la validación desde el primer eslabón
      return amountCheck.Validate(request);
    }
    protected virtual decimal CalculateFees(PaymentRequest request, decimal convertedAmount)
    {
      // Elijimos la estrategia correspondiente
      ICommissionStrategy strategy = request.CustomerType switch
      {
        "Premium" => new PremiumCommission(),
        "International" => new InternationalCommission(),
        _ => new StandardCommission()
      };

      // Aplicamos la estrategia
      decimal comission = strategy.Calculate(request.Amount);

      return request.Amount + comission;
    }
    private void ExecuteTransaction(PaymentRequest request, decimal finalAmount)
    {
      // Usamos la Factory de Gateways y el Adapter
      IPaymentGateway gateway = GatewayFactory.Get(request.PaymentMethod);

      bool success = gateway.ProcessExternalPayment(
          finalAmount,
          request.Currency,
          request.TransactionId
      );

      if (!success) throw new Exception($"Fallo en la pasarela {request.PaymentMethod}");
    }

    // Paso opcional (Hook) con implementación base
    protected virtual void SendNotifications(PaymentRequest request)
    {
      Console.WriteLine("Notificación estándar enviada.");
    }
  }
}

