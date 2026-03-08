// Security/PaymentValidator.cs
using Configuration;
namespace Security
{
  public abstract class PaymentValidator
  {
    protected PaymentValidator? Next;

    public void SetNext(PaymentValidator next) => Next = next;

    public abstract bool Validate(PaymentRequest request);
  }
}

