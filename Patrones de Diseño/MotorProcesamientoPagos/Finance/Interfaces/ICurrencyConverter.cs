// Finance/Interfaces/ICurrencyConverter.cs
using Configuration;
namespace Finance
{
  public interface ICurrencyConverter
  {
    decimal Convert(decimal amount, string targetCurrency);
  }
}