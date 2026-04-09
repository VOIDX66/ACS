using Configuration;

namespace Security.Infrastructure.Validators
{
  public abstract class PaymentValidator
  {
    protected PaymentValidator? Next;

    public void SetNext(PaymentValidator next) => Next = next;

    public abstract bool Validate(Payments.Domain.Entities.PaymentRequest request);
  }
}