// Configuration/PaymentRequest.cs
namespace Configuration
{
  // Definido como record para inmutabilidad
  public record PaymentRequest(
      string TransactionId,
      decimal Amount,
      string Currency,
      string Country,
      string CustomerType, // "Standard", "Premium", "International"
      string PaymentMethod // "CreditCard", "Crypto", etc.
  );
}