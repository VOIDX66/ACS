namespace Payments.Domain.Entities
{
  public record PaymentRequest(
      string TransactionId,
      decimal Amount,
      string Currency,
      string Country,
      string CustomerType,
      string PaymentMethod
  );
}